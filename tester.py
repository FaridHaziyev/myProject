import unittest
from createPagesWithContent import get_definitions
from createPagesWithContent import load_xml_data,get_source, get_target, get_page_actual_name, get_links 
from createPagesWithContent import get_all_pairs, get_cattegories
from createPagesWithContent import get_page_name,check_existence_in_wordnet_bool,get_possible_synsets, get_page_id
from xml.dom import minidom
from nltk.corpus import wordnet

#mock page class is create here

class Page:
    def __init__(self):
        self.page_id = None
        self.page_name = None     
        
pages = []
#-----------------------------



loaded_data = load_xml_data("data_test.xml")  
all_pairs = get_all_pairs(loaded_data)
pair1 = all_pairs[0]
source = get_source(pair1)
target = get_target(pair1)
source_actual_name = get_page_actual_name(source)
target_name = get_page_name(target)
print(target_name)
target_actual_name = get_page_actual_name(target)
definition_words = ["apple", "juice"]
page_in_wordnet = False
page_id = get_page_id(pair1)
pos_synsets = get_possible_synsets([], target_actual_name)

class PageCreationTest(unittest.TestCase):
    def test_load_xml_data(self):
        self.assertIsNotNone(
                            load_xml_data("data_test.xml")  
                            )
    
    def test_get_all_pairs(self):
        self.assertIsNotNone(
                            get_all_pairs(loaded_data)
                            )
    
    def test_get_page_id(self):
        self.assertEqual(
                        get_page_id(pair1), "1"
                        )

    def test_get_source(self):
        self.assertIsNotNone(
                            get_source(pair1)
                            )

    def test_get_target(self):
        self.assertIsNotNone(
                            get_target(pair1)
                            )
    
    def test_get_page_actual_name(self):
        self.assertEqual(
                        get_page_actual_name(source),
                        "Ryegatea (obligata)"
                        )

        self.assertEqual(
                        get_page_actual_name(target),
                        "Ryegate obligated"
                        )
    def test_get_page_name(self):
        self.assertEqual(
                        get_page_name(target),
                        "Ryegate"
                        )


    def test_check_existence_in_wordnet_bool(self):
        self.assertFalse(
                         check_existence_in_wordnet_bool(target_name)
                        )
    

    def test_get_definitions(self):
        self.assertIsNone(
                         get_definitions(target_actual_name)
                         )


    def test_get_possible_synsets(self):
        self.assertTrue(
                         not get_possible_synsets([], target_actual_name)
                         )



    def test_get_links(self):
        self.assertEqual(
                        get_links(target), 
                        {"ryegate", "vermont", "reigate", "montana"}
                        )

    def test_get_cattegories(self):
        self.assertEqual(
                        get_cattegories(target),
                        {"ala", "bula", "boz", "keçi"}
                        )



if __name__ == "__main__":
    unittest.main()
