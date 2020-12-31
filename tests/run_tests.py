import os
import shutil
from subprocess import Popen, PIPE, call
import sys
import unittest

TEST_DIR    = os.path.dirname(os.path.abspath(__file__))
ITSTOOL_DIR = os.path.dirname(TEST_DIR)
PYTHON = sys.executable or 'python3'

class ItstoolTests(unittest.TestCase):
    def tearDown(self):
        for test_file in ('test.pot', 'test.mo', 'test.xml'):
            path = os.path.join(TEST_DIR, test_file)
            if os.path.exists(path):
                os.remove(path)

    def run_command(self, cmd, expected_status=0):
        """ Helper method to run a shell command """
        # Set stdout = sys.stdout to debug a subprocess if you set a breakpoint in it
        pipe = Popen(cmd, shell=True, env=os.environ, stdin=None, stdout=PIPE, stderr=PIPE)
        (output, errout) = map(lambda x:x.decode('utf-8'), pipe.communicate())
        status = pipe.returncode
        self.assertEqual(status, expected_status, errout or output)
        return {'status': status, 'output': output, 'errors': errout}

    def assertFilesEqual(self, f1, f2):
        options = ""
        if f1.endswith(".po") or f1.endswith(".pot"):
            options = "--ignore-matching-lines=^\\\"POT-Creation-Date"
        result = self.run_command("diff -u %s %s %s" % (options, f1, f2))
        self.assertEqual(result['output'], "", result['output'])

    def _test_pot_generation(self, start_file, reference_pot=None, expected_status=0, options=None):
        start_file_base = os.path.splitext(start_file)[0]
        result = self.run_command("cd %(dir)s && %(python)s itstool_test %(opt)s -n -o %(out)s %(in)s" % {
            'python' : PYTHON,
            'dir' : ITSTOOL_DIR,
            'opt' : (options or ''),
            'out' : os.path.join('tests', "test.pot"),
            'in'  : os.path.join('tests', start_file),
        }, expected_status)
        # If we expected a failure, don't keep checking stuff
        if expected_status != 0:
            return result
        # If a reference pot file is present, test the output with this file
        if reference_pot is None:
            reference_pot = start_file_base + ".pot"
        if os.path.exists(os.path.join(TEST_DIR, reference_pot)):
            self.assertFilesEqual(os.path.join(TEST_DIR, "test.pot"), os.path.join(TEST_DIR, reference_pot))
        return result

    def _test_translation_join(self, start_file, langs, xml_file=None):
        start_file_base = os.path.splitext(start_file)[0]
        self._test_pot_generation(start_file)

        for lang in langs:
            po_file = '%s.%s.po' % (start_file_base, lang)
            mo_file = '%s.mo' % lang
            self.run_command("cd %(dir)s && msgfmt -o %(mo_file)s %(po_file)s" %
                             {'dir': TEST_DIR, 'mo_file': mo_file, 'po_file': po_file})
        result = self.run_command("cd %(dir)s && %(python)s itstool_test -n -o%(res)s -j %(src)s %(mo)s" % {
                'python' : PYTHON,
                'dir': ITSTOOL_DIR,
                'res': os.path.join(TEST_DIR, 'test.xml'),
                'src': os.path.join(TEST_DIR, start_file),
                'mo': ' '.join([os.path.join(TEST_DIR, '%s.mo' % lang) for lang in langs])
                })
        if xml_file is None:
            xml_file = '%s.joined.xml' % start_file_base
        self.assertFilesEqual(
            os.path.join(TEST_DIR, 'test.xml'),
            os.path.join(TEST_DIR, xml_file)
            )
        return result
            

    def _test_translation_process(self, start_file, expected_status=0, outputs=None, options=None):
        start_file_base = os.path.splitext(start_file)[0]
        self._test_pot_generation(start_file, options=options)

        if outputs is None:
            outputs = [("%s.ll.po" % start_file_base, "%s.ll.xml" % start_file_base, 'll')]
        for po_file, xml_file, lang in outputs:
            self.run_command("cd %(dir)s && msgfmt -o test.mo %(po_file)s" % {'dir': TEST_DIR, 'po_file': po_file}) 
            self.run_command("cd %(dir)s && %(python)s itstool_test -n %(opt)s -l %(lc)s -m %(mo)s -o %(res)s %(src)s" % {
                    'python' : PYTHON,
                    'dir': ITSTOOL_DIR,
                    'opt': (options or ''),
                    'lc' : lang,
                    'mo' : os.path.join(TEST_DIR, "test.mo"),
                    'res': os.path.join(TEST_DIR, "test.xml"),
                    'src': os.path.join(TEST_DIR, start_file),
                    }, expected_status)
            if (expected_status == 0):
                self.assertFilesEqual(
                    os.path.join(TEST_DIR, "test.xml"),
                    os.path.join(TEST_DIR, xml_file)
                    )


    def test_LocNote1(self):
        # FIXME: only the third note appears currently, as notes on subnodes don't propagate to parent nodes
        self._test_pot_generation('LocNote/LocNote1.xml')

    def test_LocNote2(self):
        # FIXME: only the third note appears currently, as notes on subnodes don't propagate to parent nodes
        self._test_pot_generation('LocNote/LocNote2.xml')

    def test_LocNote3(self):
        self._test_pot_generation('LocNote/LocNote3.xml')

    def test_LocNote4(self):
        self._test_pot_generation('LocNote/LocNote4.xml')

    def test_EX_locNote_element_1(self):
        self._test_pot_generation('LocNote/EX-locNote-element-1.xml')

    def test_EX_locNote_selector_2(self):
        self._test_pot_generation('LocNote/EX-locNote-selector-2.xml')

    def test_EX_locNotePointer_attribute_1(self):
        self._test_pot_generation('LocNote/EX-locNotePointer-attribute-1.xml')

    def test_EX_locNoteRef_attribute_1(self):
        self._test_pot_generation('LocNote/EX-locNoteRef-attribute-1.xml')

    def test_EX_locNoteRefPointer_attribute_1(self):
        self._test_pot_generation('LocNote/EX-locNoteRefPointer-attribute-1.xml')

    def test_PreserveSpace1(self):
        self._test_pot_generation('preservespace1xml.xml')

    def test_PreserveSpace2(self):
        self._test_pot_generation('preservespace2xml.xml')

    def test_PreserveSpace3(self):
        self._test_pot_generation('preservespace3xml.xml')

    def test_PreserveSpace4(self):
        self._test_pot_generation('preservespace4xml.xml')

    def test_PreserveSpace5(self):
        self._test_translation_process('preservespace5xml.xml')

    def test_Translate1(self):
        self._test_translation_process('Translate/Translate1.xml')

    def test_Translate2(self):
        self._test_translation_process('Translate/Translate2.xml')

    def test_Translate3(self):
        self._test_translation_process('Translate/Translate3.xml')

    def test_Translate4(self):
        self._test_translation_process('Translate/Translate4.xml')

    def test_Translate5(self):
        self._test_translation_process('Translate/Translate5.xml')

    def test_Translate6(self):
        self._test_translation_process('Translate/Translate6.xml')

    def test_Translate7(self):
        self._test_translation_process('Translate/Translate7.xml')

    def test_TranslateGlobal(self):
        self._test_translation_process('Translate/TranslateGlobal.xml')

    def test_ExternalResource1(self):
        self._test_pot_generation('ExternalResource/ExternalResource1Xml.xml')

    def test_ExternalResource2(self):
        self._test_pot_generation('ExternalResource/ExternalResource2Xml.xml')

    def test_ExternalResource3(self):
        self._test_pot_generation('ExternalResource/ExternalResource3Xml.xml')

    def test_ExternalResource1Attr(self):
        self._test_pot_generation('ExternalResource/Attr/ExternalResource1AttrXml.xml')

    def test_ExternalResource2Attr(self):
        self._test_pot_generation('ExternalResource/Attr/ExternalResource2AttrXml.xml')

    def test_ExternalResource3Attr(self):
        self._test_pot_generation('ExternalResource/Attr/ExternalResource3AttrXml.xml')

    def test_IdValue1(self):
        self._test_pot_generation('IdValue/idvalue1xml.xml')

    def test_IdValue2(self):
        self._test_pot_generation('IdValue/idvalue2xml.xml')

    def test_IdValue3(self):
        self._test_pot_generation('IdValue/idvalue3xml.xml')

    def test_Locale1(self):
        self._test_translation_process('LocaleFilter/Locale1Xml.xml',
                                       outputs=[('LocaleFilter/Locale1Xml.fr_FR.po',
                                                 'LocaleFilter/Locale1Xml.fr_FR.xml',
                                                 'fr-FR'),
                                                ('LocaleFilter/Locale1Xml.fr_CA.po',
                                                 'LocaleFilter/Locale1Xml.fr_CA.xml',
                                                 'fr-CA'),
                                                ('LocaleFilter/Locale1Xml.fr_CH.po',
                                                 'LocaleFilter/Locale1Xml.fr_CH.xml',
                                                 'fr-CH')])

    def test_Locale2(self):
        self._test_translation_process('LocaleFilter/Locale2Xml.xml',
                                       outputs=[('LocaleFilter/Locale2Xml.fr_FR.po',
                                                 'LocaleFilter/Locale2Xml.fr_FR.xml',
                                                 'fr-FR'),
                                                ('LocaleFilter/Locale2Xml.fr_CA.po',
                                                 'LocaleFilter/Locale2Xml.fr_CA.xml',
                                                 'fr-CA'),
                                                ('LocaleFilter/Locale2Xml.fr_CH.po',
                                                 'LocaleFilter/Locale2Xml.fr_CH.xml',
                                                 'fr-CH')])

    def test_Locale3(self):
        self._test_translation_process('LocaleFilter/Locale3Xml.xml',
                                       outputs=[('LocaleFilter/Locale3Xml.fr_FR.po',
                                                 'LocaleFilter/Locale3Xml.fr_FR.xml',
                                                 'fr-FR'),
                                                ('LocaleFilter/Locale3Xml.fr_CA.po',
                                                 'LocaleFilter/Locale3Xml.fr_CA.xml',
                                                 'fr-CA'),
                                                ('LocaleFilter/Locale3Xml.fr_CH.po',
                                                 'LocaleFilter/Locale3Xml.fr_CH.xml',
                                                 'fr-CH')])

    def test_Locale4(self):
        self._test_translation_process('LocaleFilter/Locale4Xml.xml',
                                       outputs=[('LocaleFilter/Locale4Xml.fr_FR.po',
                                                 'LocaleFilter/Locale4Xml.fr_FR.xml',
                                                 'fr-FR'),
                                                ('LocaleFilter/Locale4Xml.fr_CA.po',
                                                 'LocaleFilter/Locale4Xml.fr_CA.xml',
                                                 'fr-CA'),
                                                ('LocaleFilter/Locale4Xml.fr_CH.po',
                                                 'LocaleFilter/Locale4Xml.fr_CH.xml',
                                                 'fr-CH')])

    def test_Locale5(self):
        self._test_translation_process('LocaleFilter/Locale5Xml.xml',
                                       outputs=[('LocaleFilter/Locale5Xml.fr_FR.po',
                                                 'LocaleFilter/Locale5Xml.fr_FR.xml',
                                                 'fr-FR'),
                                                ('LocaleFilter/Locale5Xml.fr_CA.po',
                                                 'LocaleFilter/Locale5Xml.fr_CA.xml',
                                                 'fr-CA'),
                                                ('LocaleFilter/Locale5Xml.fr_CH.po',
                                                 'LocaleFilter/Locale5Xml.fr_CH.xml',
                                                 'fr-CH')])

    def test_Locale6(self):
        self._test_translation_process('LocaleFilter/Locale6Xml.xml',
                                       outputs=[('LocaleFilter/Locale6Xml.fr_FR.po',
                                                 'LocaleFilter/Locale6Xml.fr_FR.xml',
                                                 'fr-FR'),
                                                ('LocaleFilter/Locale6Xml.fr_CA.po',
                                                 'LocaleFilter/Locale6Xml.fr_CA.xml',
                                                 'fr-CA'),
                                                ('LocaleFilter/Locale6Xml.fr_CH.po',
                                                 'LocaleFilter/Locale6Xml.fr_CH.xml',
                                                 'fr-CH')])

    def test_Locale1_join(self):
        self._test_translation_join('LocaleFilter/Locale1Xml.xml',
                                    ('fr_FR', 'fr_CA', 'fr_CH'))

    def test_Locale2_join(self):
        self._test_translation_join('LocaleFilter/Locale2Xml.xml',
                                    ('fr_FR', 'fr_CA', 'fr_CH'))

    def test_Locale3_join(self):
        self._test_translation_join('LocaleFilter/Locale3Xml.xml',
                                    ('fr_FR', 'fr_CA', 'fr_CH'))

    def test_Locale4_join(self):
        self._test_translation_join('LocaleFilter/Locale4Xml.xml',
                                    ('fr_FR', 'fr_CA', 'fr_CH'))

    def test_Locale5_join(self):
        self._test_translation_join('LocaleFilter/Locale5Xml.xml',
                                    ('fr_FR', 'fr_CA', 'fr_CH'))

    def test_Locale6_join(self):
        self._test_translation_join('LocaleFilter/Locale6Xml.xml',
                                    ('fr_FR', 'fr_CA', 'fr_CH'))

    def test_elementwithintextlocalitsSpanXml(self):
        self._test_translation_process('elementwithintextlocalitsSpanXml.xml')

    def test_elementwithintextLocalXml(self):
        self._test_translation_process('elementwithintextLocalXml.xml')

    def test_WithinText1(self):
        self._test_translation_process('WithinText1.xml')

    def test_WithinText2(self):
        self._test_translation_process('WithinText2.xml')

    def test_IT_externalRef1(self):
        self._test_translation_process('IT-externalRef1.xml')

    def test_IT_locNote_inline(self):
        self._test_pot_generation('IT-locNote-inline.xml')

    def test_IT_locNote_multiples(self):
        self._test_pot_generation('IT-locNote-multiples.xml')

    # **** custom itst rules ****
    def test_IT_dropRule_1(self):
        self._test_translation_process('IT-dropRule-1.xml')

    def test_IT_attributes_1(self):
        self._test_translation_process('IT-attributes-1.xml')

    def test_IT_attributes_2(self):
        self._test_translation_process('IT-attributes-2.xml')

    def test_IT_context_1(self):
        self._test_translation_process('IT-context-1.xml')

    def test_IT_placeholder_1(self):
        self._test_translation_process('IT-placeholder-1.xml')

    def test_IT_prefixes_1(self):
        self._test_translation_process('IT-prefixes-1.xml')

    def test_IT_malformed(self):
        """ Test that a malformed XML generates a proper exception """
        res = self._test_pot_generation('IT-malformed.xml', expected_status=1)
        #self.assertTrue("libxml2.parserError" in res['errors'])

    def test_IT_translate_with_external_dtds_malformed(self):
        """ Test that parsing XML requiring external DTD generates exception """
        res = self._test_pot_generation('IT-uses-external-dtds.xml', expected_status=1)

    def test_IT_translate_with_external_dtds(self):
        self._test_translation_process('IT-uses-external-dtds.xml', options='--load-dtd')

    # FIXME: It would be nice to be able to do this without loading the
    # external subset, but libxml2 seems to verify entity references even
    # if it doesn't do substitution.
    def test_IT_keep_entities_1(self):
        self._test_translation_process('IT-keep-entities-1.xml',
                                       options='--load-dtd --keep-entities')

    def test_IT_keep_entities_2(self):
        self._test_translation_process('IT-keep-entities-2.xml', options='--keep-entities')

    def test_IT_join_1(self):
        self._test_translation_join('IT-join-1.xml', ('cs', 'de', 'fr'))

    def test_Translate3_wrong1(self):
        """ Test that bad XML syntax in translation generates a proper exception """
        self._test_translation_process('Translate/Translate3.xml', expected_status=1,
                                       outputs=[('Translate/Translate3.ll.wrong.po', None, 'll')],
                                       options='-s')
        #self.assertTrue("libxml2.parserError" in res['errors'])

    def test_Translate3_wrong2(self):
        """ Test that bad XML syntax in translation is handled gracefully """
        self._test_translation_process('Translate/Translate3.xml',
                                       outputs=[('Translate/Translate3.ll.wrong.po',
                                                 'Translate/Translate3.ll.wrong.xml',
                                                 'll')])


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

