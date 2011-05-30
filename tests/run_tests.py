import os
import shutil
from subprocess import Popen, PIPE, call
import unittest

TEST_DIR    = os.path.dirname(os.path.abspath(__file__))
ITSTOOL_DIR = os.path.dirname(TEST_DIR)

class ItstoolTests(unittest.TestCase):
    def tearDown(self):
        for test_file in ('test.pot', 'test.mo', 'test.xml'):
            path = os.path.join(TEST_DIR, test_file)
            if os.path.exists(path):
                os.remove(path)

    def run_command(self, cmd):
        """ Helper method to run a shell command """
        pipe = Popen(cmd, shell=True, env=os.environ, stdin=None, stdout=PIPE, stderr=PIPE)
        (output, errout) = pipe.communicate()
        status = pipe.returncode
        self.assertEqual(status, 0, errout or output)
        return (status, output, errout)

    def assertFilesEqual(self, f1, f2):
        options = ""
        if f1.endswith(".po") or f1.endswith(".pot"):
            options = "--ignore-matching-lines=^\\\"POT-Creation-Date"
        result = self.run_command("diff -u %s %s %s" % (options, f1, f2))
        return self.assertEqual(result[1], "", result[1])

    def test_unicode_markup(self):
        result = self.run_command("cd %(dir)s && python itstool_test -o %(out)s %(in)s" % {
            'dir' : ITSTOOL_DIR,
            'out' : os.path.join('tests', "test.pot"),
            'in'  : os.path.join('tests', 'Translate1.xml'),
        })
        self.assertFilesEqual(os.path.join(TEST_DIR, "test.pot"), os.path.join(TEST_DIR, "Translate1.pot"))

        # Compile mo and merge
        self.run_command("cd %(dir)s && msgfmt -o test.mo Translate1.ll.po" % {'dir': TEST_DIR}) 
        res = self.run_command("cd %(dir)s && python itstool_test -m %(mo)s -o %(res)s %(src)s" % {
            'dir': ITSTOOL_DIR,
            'mo' : os.path.join(TEST_DIR, "test.mo"),
            'res': os.path.join(TEST_DIR, "test.xml"),
            'src': os.path.join(TEST_DIR, "Translate1.xml"),
        })
        self.assertFilesEqual(os.path.join(TEST_DIR, "test.xml"), os.path.join(TEST_DIR, "Translate1.ll.xml"))


class ITSTestRunner(unittest.TextTestRunner):
    def run(self, test):
        # Global setup
        test_binary_path = os.path.join(ITSTOOL_DIR, "itstool_test")
        shutil.copy(os.path.join(ITSTOOL_DIR, "itstool.in"), test_binary_path)
        data_dir = os.path.join(ITSTOOL_DIR, "its")
        call("sed -i -e 's/@DATADIR@/%s/' %s" % (data_dir.replace('/', '\/'), test_binary_path), shell=True)

        result = super(ITSTestRunner, self).run(test)

        os.remove(test_binary_path)
        return result


if __name__ == '__main__':
    unittest.main(testRunner=ITSTestRunner)

