
from .utils import validate_tag_name
from .exceptions import FilterSyntaxError, InvalidTagName

class FtagFilterExpressionToken(object):
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos
    def __str__(self):
        return self.token
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.token)

class FtagGroupStartOperator(FtagFilterExpressionToken):
    OP_CHAR = '('
    OP_TYPE = 'grouping'

class FtagGroupEndOperator(FtagFilterExpressionToken):
    OP_CHAR = ')'
    OP_TYPE = 'grouping'

class FtagOrOperator(FtagFilterExpressionToken):
    OP_CHAR = ','
    OP_PREC = 4
    OP_ASSOC = 'L'          # https://en.wikipedia.org/wiki/Operator_associativity
    OP_TYPE = 'binary'

    def eval(self, val0, val1):
        return val0 or val1


class FtagAndOperator(FtagFilterExpressionToken):
    OP_CHAR = '+'
    OP_PREC = 3
    OP_ASSOC = 'L'
    OP_TYPE = 'binary'

    def eval(self, val0, val1):
        return val0 and val1


class FtagNotOperator(FtagFilterExpressionToken):
    OP_CHAR = '~'
    OP_PREC = 5
    OP_ASSOC = 'R'
    OP_TYPE = 'unary'

    def eval(self, val0):
        return not val0


class FtagTagOperator(FtagFilterExpressionToken):
    '''Match a tag name'''
    OP_CHAR = None
    OP_PREC = 0
    OP_ASSOC = 'L'
    OP_TYPE = 'match'

    def matches(self, path):
        '''
        Check path has tag

        :param path: TaggablePath
        :return: bool
        '''
        tag = self.token
        return tag in path.tags


class FtagFilterExpression(object):
    '''
    Expression evaluator for filtering paths based on tags

    Ftag filters are basic infix like expressions used to match
    paths (file or directories) based on the tags assigned to that
    path.  Used in commands such as list and exec to act on a
    subset of files.

    Examples:
        base            --> Any path with base tag
        notag,base      --> Any path with notag OR base tags
        base+new        --> Any path with base AND new tags
        base+~new       --> Any path with base tag, but not new tag

    Operators in order of precedence
        ()  Grouping (or precedence override)
        ,   OR operator
        +   AND operator
        ~   NEGATION operator
    '''

    def __init__(self, filter_expression):
        self.__exp = filter_expression
        self.exp_postfix_stack = list(self._compile_expression())


    @property
    def exp(self):
        return self.__exp


    def __str__(self):
        return self.__exp


    def __repr__(self):
        return "FtagFilterExpression('%s')" % (self.__exp)


    def matches(self, path):
        '''
        Check if path matches the filter

        :param path: TaggablePath
        :return: bool
        '''
        eval_stack = list()
        for op in self.exp_postfix_stack:
            if op.OP_TYPE == 'match':
                eval_stack.append(op.matches(path))
            elif op.OP_TYPE == 'binary':
                if len(eval_stack) < 2:
                    raise FilterSyntaxError(
                        msg = "Operator %s requires two values" % (op.token),
                        expression = self.exp,
                        pos = op.pos)
                eval_stack.append(op.eval(eval_stack.pop(), eval_stack.pop()))
            elif op.OP_TYPE == 'unary':
                if len(eval_stack) < 1:
                    raise FilterSyntaxError(
                        msg = "Operator %s requires one value" % (op.token),
                        expression = self.exp,
                        pos = op.pos)
                eval_stack.append(op.eval(eval_stack.pop()))
            else:
                raise Exception("Unknown operator type: " + op.OP_TYPE)

        if len(eval_stack) != 1:
            FilterSyntaxError(
                msg = "Failed to interpret filter expression (internal error.  missing operator?)",
                expression = self.exp,
                pos = 0)
        return eval_stack.pop()


    def _compile_expression(self):
        '''
        Take string expression and build a postfix processing queue

        Compiles self.__exp into self.exp_postfix_stack

        Using Shunting-yard algorithm
        https://en.wikipedia.org/wiki/Shunting-yard_algorithm
         - "Numbers" are FtagTagOperator which match paths and return bools
         - self.exp_postfix_stack is the intended output stack
        '''
        op_stack = list()
        token = None

        def _should_pop_op_stack():
            if len(op_stack) > 0:
                top = op_stack[-1]
                # the operator at the top of the stack is not a left bracket
                if top.__class__ is FtagGroupStartOperator:
                    return False
                # there is an operator at the top of the operator stack with greater
                # precedence
                if top.OP_PREC > token.OP_PREC:
                    return True
                # the operator at the top of the operator stack has equal precedence
                # and the operator is left associative
                if top.OP_PREC == token.OP_PREC and top.OP_ASSOC == 'L':
                    return True

        for token in self._tokenize(self.__exp):
            if token.__class__ is FtagTagOperator:
                yield token
            elif token.__class__ is FtagGroupStartOperator:
                op_stack.append(token)
            elif token.__class__ is FtagGroupEndOperator:
                while len(op_stack) > 0 and op_stack[-1].__class__ is not FtagGroupStartOperator:
                    yield op_stack.pop()
                if len(op_stack) == 0:
                    raise FilterSyntaxError(
                        msg = "Missing left parentheses",
                        expression = self.exp,
                        pos = token.pos)
                op_stack.pop()
            else:  # token is an operator
                # pop operators from the operator stack, onto the output queue.
                while _should_pop_op_stack():
                    yield op_stack.pop()
                # push the read operator onto the operator stack.
                op_stack.append(token)

        # Done reading tokens.  Pop the remainin op stack
        while len(op_stack) > 0:
            if op_stack[-1].__class__ is FtagGroupStartOperator or op_stack[-1].__class__ is FtagGroupEndOperator:
                raise FilterSyntaxError(
                    msg = "Unmatched parentheses",
                    expression = self.exp,
                    pos = len(self.exp))
            yield op_stack.pop()


    VALID_OPERATORS = (
        FtagGroupStartOperator.OP_CHAR,
        FtagGroupEndOperator.OP_CHAR,
        FtagOrOperator.OP_CHAR,
        FtagAndOperator.OP_CHAR,
        FtagNotOperator.OP_CHAR,
    )

    def _tokenize(self, exp):
        '''Tokenize self.__exp (lexer)'''
        tag_exp = None
        for i, c in enumerate(exp):
            if c in self.VALID_OPERATORS:

                # Yield tag matching expression we've been collecting
                if tag_exp is not None:
                    try:
                        validate_tag_name(tag_exp.token)
                    except InvalidTagName, e:
                        raise FilterSyntaxError(
                            msg = str(e),
                            expression = exp,
                            pos = tag_exp.pos)
                    yield tag_exp
                    tag_exp = None

                # Interpret operator
                if c == FtagGroupStartOperator.OP_CHAR:
                    yield FtagGroupStartOperator(c, i)
                elif c == FtagGroupEndOperator.OP_CHAR:
                    yield FtagGroupEndOperator(c, i)
                elif c == FtagOrOperator.OP_CHAR:
                    yield FtagOrOperator(c, i)
                elif c == FtagAndOperator.OP_CHAR:
                    yield FtagAndOperator(c, i)
                elif c == FtagNotOperator.OP_CHAR:
                    yield FtagNotOperator(c, i)
                else:
                    raise Exception("Not a valid operator '%s'.  Update VALID_OPERATORS" % (c))

            else:

                # Collect into tag name
                if tag_exp is None:
                    tag_exp = FtagTagOperator(c, i)
                else:
                    tag_exp.token += c

        # Yield tag matching expression we've been collecting (final)
        if tag_exp is not None:
            try:
                validate_tag_name(tag_exp.token)
            except InvalidTagName, e:
                raise FilterSyntaxError(
                    msg = str(e),
                    expression = exp,
                    pos = tag_exp.pos)
            yield tag_exp





