from ftaglib import FtagExplorer

if __name__ == '__main__':
    exp = FtagExplorer()
    f = exp.get('./test/test.txt')
    if 'test' in f.tags:
        print("Hit")
    print "existing tags: " + ', '.join(f.tags)
    f.tags.add('test')