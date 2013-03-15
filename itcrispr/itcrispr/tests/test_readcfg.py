import os
import sys
import unittest
import ConfigParser
import fnmatch

SCRIPT_PATH = r"C:\Users\vimal\Workspace\itcrispr"
sys.path.append(SCRIPT_PATH)

DATADIR = os.path.join(SCRIPT_PATH, "itcrispr", "tests", "data")
sys.stderr = open(os.path.join(DATADIR, "test_readcfg.txt"), "w")
CFG_DEFS = {
    "DATABASES": {"type": "list", "value": []},
    "EXPERIMENTS": {"type": "list", "value": []},
    "EXTENSION": {"type": "string", "value": ""},
    "PRIMER_PATH": {"type": "string", "value": ""}
    }


def read_config(cfg_file):
    """Read configuration from itcrispr.cfg"""
    cfg = {"DATABASES": [], "EXPERIMENTS": [], "EXTENSION": "",
           "PRIMER_PATH": ""}

    config = ConfigParser.RawConfigParser()
    config.readfp(open(cfg_file))

    for item in cfg:
        value = ""
        try:
            value = config.get("configuration", item)
        except ConfigParser.NoOptionError:
            print "{0} is not defined in configuration file".format(item)
            raise

        if not len(value):
            print "Cannot read {0} from configuration file. "\
            "Is it defined?".format(item)
            raise ConfigParser.Error

        if CFG_DEFS[item]["type"] == "string":
            cfg[item] = value
        elif CFG_DEFS[item]["type"] == "list":
            cfg[item] = value.split(",")

    return cfg


class TestReadCfg(unittest.TestCase):

    def testSuccessRead(self):
        """If all values are present, configuration should be read properly."""
        good_cfg = os.path.join(DATADIR, "good_cfg.cfg")
        c = read_config(good_cfg)
        self.assertEqual(c["DATABASES"], ["CRISPRBN6", "vimal"])
        self.assertEqual(c["EXPERIMENTS"], ["CRISPR1", "CRISPR2"])
        self.assertEqual(c["EXTENSION"], "txt")
        self.assertEqual(fnmatch.fnmatch(c["PRIMER_PATH"], r"c:/python26/lib/"\
                                         "site-packages/itcrispr/tests/data/"\
                                         "primers"), True)

    def testFailedRead(self):
        """If an option is missing, we should not continue."""
        bad_cfg = os.path.join(DATADIR, "bad_cfg.cfg")
        self.assertRaises(ConfigParser.Error, read_config, bad_cfg)

suite = unittest.TestLoader().loadTestsFromTestCase(TestReadCfg)
unittest.TextTestRunner(stream=sys.stderr, verbosity=3).run(suite)
sys.stderr.flush()
