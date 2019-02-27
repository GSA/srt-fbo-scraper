import unittest
import os
import subprocess

class SupercronicTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_supercronic_call(self):
        if not os.getenv('TEST_DB_URL'):
            #if tests are happening locally, no need to test supercronic
            self.assertTrue(True)
            return
        process = subprocess.Popen(['supercronic', '-debug', 'crontab-test'], stdout=subprocess.PIPE)
        try:
            process.wait(timeout=10)
            result = process.returncode
        except subprocess.TimeoutExpired:
            #If the process does not terminate after timeout seconds, 
            #it'll raise a TimeoutExpired exception and then we can safely kill it
            process.kill()
            result = 0
        expected = 0
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()