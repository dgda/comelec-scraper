from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# GOOGLE CHROME VERSION USED: https://chromedriver.storage.googleapis.com/101.0.4951.41/

class Driver(object):
    __COMELEC_URL = "https://2022electionresults.comelec.gov.ph"

    def __init__(self):
        """
        Initialize the automated browser
        """
        self.__browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.__browser.maximize_window()

    def open(self) -> None:
        """
        Open the url
        """
        logging.info(f"Opening browser to url {Driver.__COMELEC_URL}")
        self.__browser.get(Driver.__COMELEC_URL)

    def get_element_by_text(self, text:str = None) -> bool:
        """
        Retrieve the element from the website by searching the text
        """
        return self.__browser.find_element_by_xpath(f"//*[contains(text(), '{text}')]")

    def if_text_visible(self, text:str = None) -> bool:
        if text is None:
            return False
        element = self.get_element_by_text(text)
        return element.is_displayed()

    def __click_element_then_wait(self, element) -> None:
        element.click()
        self.__wait(5)

    def __wait(self, seconds:int = 2) -> None:
        time.sleep(seconds)

    def close(self) -> None:
        logging.info("Closing browser")
        print("Closing browser")
        self.__browser.quit()

    def reset_dropdown(self, dropdown) -> list:
        dropdown.click()
        self.__wait(1)
        dropdown_input = dropdown.find_element_by_xpath(".//input")
        dropdown_input.send_keys(Keys.CONTROL + "a")
        dropdown_input.send_keys(Keys.DELETE)
        self.__wait(1)
        return dropdown.find_elements_by_xpath(".//li[contains(@class, 'region-suggestion')]")


    def demo(self) -> None:
        try:
            self.open()
            self.__wait(5)
            er_results_button = self.get_element_by_text("ER Results")
            self.__click_element_then_wait(er_results_button)
            dropdowns = self.__browser.find_elements_by_class_name("region-name-wrapper")
            region = dropdowns[1]
            province = dropdowns[2]
            city = dropdowns[3]
            barangay = dropdowns[4]
            precinct_cluster = dropdowns[5]
            region.click()
            self.__wait(1)

            # Index settings just in case browser session ends midway
            region_start_index = 0
            province_start_index = 2
            city_start_index = 4
            barangay_start_index = 36
            pcid_start_index = 0


            regions = region.find_elements_by_xpath(".//li[contains(@class, 'region-suggestion')]")
            # For each region
            for i in range(region_start_index, len(regions)):
                logging.info(f"Selected region: {regions[i].text}")
                print(f"Selected region: [{i}]{regions[i].text}")
                regions[i].click()
                self.__wait(1)
                province.click()
                self.__wait(1)
                provinces = province.find_elements_by_xpath(".//li[contains(@class, 'region-suggestion')]")
                # For each province
                for j in range(province_start_index, len(provinces)):
                    logging.info(f"Selected province: {provinces[j].text}")
                    print(f"Selected province: [{j}]{provinces[j].text}")
                    provinces[j].click()
                    self.__wait(1)
                    city.click()
                    self.__wait(1)
                    cities = city.find_elements_by_xpath(".//li[contains(@class, 'region-suggestion')]")
                    # For each city
                    for k in range(city_start_index, len(cities)):
                        logging.info(f"Selected city: {cities[k].text}")
                        print(f"Selected city: [{k}]{cities[k].text}")
                        cities[k].click()
                        self.__wait(1)
                        barangay.click()
                        self.__wait(1)
                        barangays = barangay.find_elements_by_xpath(".//li[contains(@class, 'region-suggestion')]")
                        # For each barangay
                        for w in range(barangay_start_index, len(barangays)):
                            logging.info(f"Selected barangay: {barangays[w].text}")
                            print(f"Selected barangay: [{w}]{barangays[w].text}")
                            barangays[w].click()
                            self.__wait(1)
                            precinct_cluster.click()
                            self.__wait(1)
                            precinct_clusters = precinct_cluster.find_elements_by_xpath(".//li[contains(@class, 'region-suggestion')]")
                            # For each clustered precinct
                            for l in range(pcid_start_index, len(precinct_clusters)):
                                logging.info(f"Selected precinct cluster: {precinct_clusters[l].text}")
                                print(f"Selected precinct cluster: [{l}]{precinct_clusters[l].text}")
                                print(f"Indexes: [{i},{j},{k},{w},{l}]")
                                precinct_clusters[l].click()
                                self.__wait(3)
                                with open(f"output{i}.csv", "a+") as output:
                                    try:
                                        machine_id_span = self.get_element_by_text("Machine ID")
                                        common_information_container = machine_id_span.find_element_by_xpath("../../..")
                                        # For each common information
                                        for div in common_information_container.find_elements_by_xpath("div"):
                                            _div = div.find_element_by_xpath("div")
                                            __div = _div.find_elements_by_xpath("div")
                                            text = f"{__div[1].text}"
                                            output.write(f"{text},")

                                        # For each candidate
                                        candidates = ["ROBREDO,", "MARCOS,", "PANGILINAN,", "DUTERTE,"]
                                        for candidate in candidates:
                                            candidate_span = self.get_element_by_text(candidate)
                                            candidate_parent = candidate_span.find_element_by_xpath("../../..")
                                            votes_div = candidate_parent.find_elements_by_xpath("div")[1]
                                            _votes_div = votes_div.find_element_by_xpath("div")
                                            votes_span = _votes_div.find_element_by_xpath("span")
                                            output.write(f"{votes_span.text},")
                                        output.write("\n")
                                        logging.info("Wrote new data in output")
                                        print("Wrote new data in output")
                                    except Exception as e:
                                        # Some precincts don't have uploaded ERs yet as of May 13, 2022
                                        logging.error("No data found for this precinct")
                                        logging.error(e)
                                        output.write("\n")


                # Reset dropdowns so that they reattach to the DOM
                                precinct_clusters = self.reset_dropdown(precinct_cluster)
                            barangays = self.reset_dropdown(barangay)
                        cities = self.reset_dropdown(city)
                    provinces = self.reset_dropdown(province)
                regions = self.reset_dropdown(region)
            print("scraping done")
            self.__wait(10)
        except Exception as e:
            logging.error("page failed to load")
            logging.error(e)
        self.close()

def trim(string:str = "") -> str:
    return string.strip()

def cleanup() -> None:
    """
    Utility Function to remove unneccessary precinct numbers from data
    """
    lines = []
    _lines = []
    with open("z.csv", "r") as f:
        with open("t.csv", "w") as _f:
            for line in f:
                if line not in lines:
                    cleaned_data = [x for x in map(trim, line.split(",")) if not ((len(x) == 5 or len(x) == 6) and x.isalnum() and not x.isalpha())]
                    cleaned_data_string = ",".join(cleaned_data)
                    lines.append(cleaned_data[0])
                    _lines.append(cleaned_data_string)
                    _f.write(f"{cleaned_data_string}\n")
                if line.split(",")[0] in lines:
                    print(line.split(",")[0])

if __name__ == "__main__":
    logging.basicConfig(level=None)
    driver = Driver()
    driver.demo()
