# TwitterMatcher

TwitterMatcher application that allows do to syntagmatic analysis for term on twitter Feed. This application captures, cleans and stores tweets for a twitter feed to do further analysis. Once the data is available the main class provides all the logic to calculate mutual information and entropy for the tokens in the text. Syntagmatic relationships are found calculating the mutual information using a KL-divergence algorithm and using the IDF and TF to determine the tokens with the highest mutual information from the capture text.
