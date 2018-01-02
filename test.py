from ftaglib import FtagExplorer, FtagFilterExpression, FilterSyntaxError

if __name__ == '__main__':

    f = FtagFilterExpression("(drupal_base+(module,~library)),notag")

    exp = FtagExplorer()
    path = exp.get('test/live/sites/README.txt')
    print(f.matches(path))

    try:
        f = FtagFilterExpression("(drupal_base+(module-,~library)),notag")
        f.matches(path)
    except FilterSyntaxError, e:
        print(str(e))
