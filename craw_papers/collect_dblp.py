import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm

years = [2016,2017,2018,2019,2020,2021,2022,2023,2024]
years = [2020,2021,2022,2023,2024]

confs = [
        'sigmod','pods','vldb','icde', # Database
        'www','wsdm', # World Wide Web
        'acl','naacl','colingconf','eacl','conll','emnlp', 'lrec', 'wmt', 'semeval', 'conll', 'slt', 'blackboxnlp', 'sigdial', 'inlg', 'rep4nlp', 'bea', # NLP
        'kdd','icdm','cikm','pkdd','pakdd','sdm', # Data Mining
        'bigdataconf', # Big Data
        'sigir','jcdl','ecir','icadl', # Information Retrieval
        'aaai','ijcai','uai','aistats','ecai', # Artificial Intelligence
        'mm', # Multimedia
        'iros','icra','atal','corl','rss', # Robotics & Reinforcement Learning
        'cvpr','iccv','eccv','wacv','siggraph','siggrapha', # Computer Vision
        'nips','icml','iclr', # Machine Learning
        'interspeech','icassp' # Speech
        'sp','tifsconf','ccs','uss','ndss', # Security
        'fat', # ACM Conference on Fairness, Accountability and Transparency (FAccT)
        'isaga', 'gdn', # Game Theory and Decision Theory
        'cdc', # Automation & Control Theory
        'chi','iui','hri','ACMdis', # Human-Computer Interaction
        'ssci','gecco','cec' # Evolution Computation
        ]

journals = [
            # Artificial Intelligence
            "ai", # Artificial Intelligence
            "eswa", # Expert Systems with Applications
            "tnn", # IEEE Transactions on Neural Networks and Learning Systems
            "tcyb", # IEEE Transactions on Systems, Man, and Cybernetics
            "natmi", # Nature Machine Intelligence
            "pr", # Neural Networks
            "ijon", # Neurocomputing
            "jmlr", # Journal of Machine Learning Research
            "tfs", # IEEE Transactions on Fuzzy Systems
            "nca", # Neural Computing and Applications
            "apin", # Applied Intelligence
            # Automation & Control Theory
            "tac", # IEEE Transactions on Automatic Control
            "automatica", # Automatica
            "ieeejas", # IEEE/CAA Journal of Automatica Sinica
            "tcst", # IEEE Transactions on Control Systems Technology
            "tcns", # IEEE Transactions on Control of Network Systems
            "jirs", # Journal of Intelligent and Robotic Systems
            # Language
            "colingjour", # Computational Linguistics
            "tacl", # Transactions of the Association for Computational Linguistics
            "csl", # Computer Speech & Language
            "talip", # ACM Transactions on Asian and Low-Resource Language Information Processing
            "lre", # Language Resources and Evaluation
            # Pattern Recognition & Signal Processing
            "tsp", # IEEE Transactions on Signal Processing
            "tcsv", # IEEE Transactions on Circuits and Systems for Video Technology
            "taslp", # IEEE/ACM Transactions on Audio, Speech and Language Processing
            "jstsp", # IEEE Journal of Selected Topics in Signal Processing
            "pami", # IEEE Transactions on Pattern Analysis and Machine Intelligence
            # Computer Vision & Graphics
            "tip", # IEEE Transactions on Image Processing
            "ijcv", # International Journal of Computer Vision
            "icip", # IEEE International Conference on Image Processing
            "jvcir", # Journal of Visual Communication and Image Representation
            "paa", # Pattern Analysis and Applications
            "tmi", # IEEE transactions on medical imaging
            "mia", # Medical Image Analysis
            "tvcg", # IEEE Transactions on Visualization and Computer Graphics
            "tog", # ACM Transactions on Graphics
            "cgf", # Computer Graphics Forum
            # Security
            "compsec", # Computers & Security
            "ieeesp", # IEEE Security & Privacy
            "tdsc", # IEEE Transactions on Dependable and Secure Computing
            "tifsjour", # IEEE Transactions on Information Forensics and Security
            "istr", # Journal of Information Security and Applications
            # Survey & Review
            "csur", # ACM Computing Surveys
            "air", # Artificial Intelligence Review
            "igtr", # International Game Theory Review
            "arcras", # Annual Review of Control, Robotics, and Autonomous Systems
            "arc", # Annual Reviews in Control
            "widm", # WIREs Data Mining and Knowledge Discovery
            "rsl", # The Review of Symbolic Logic
            "rss", # The Review of Socionetwork Strategies
            "intpolrev", # Internet Policy Review
            "nrhm", # New Review of Hypermedia and Multimedia
            "oir", # Online Information Review
            "siamrev", # SIAM Review
            "ker", # The Knowledge Engineering Review
            # Big Data & Data Mining
            "sigkdd", # SIGKDD Explorations
            "kbs", # Knowledge-Based Systems
            "snam", # Social Network Analysis and Mining
            "jbd", # Journal of Big Data
            "kais", # Knowledge and Information Systems
            "tist", # ACM Transactions on Intelligent Systems and Technology
            "datamine", # Data Mining and Knowledge Discovery
            "tkde", # IEEE Transactions on Knowledge and Data Engineering
            "bigdatama", # Big Data Mining and Analytics
            "ipm", # Information Processing & Management
            "semweb", # Semantic Web
            # Game Theory
            "geb", # Journal of Economic Behavior & Organization
            "sigecom", # ACM Conference on Economics and Computation
            "dsj", # Decision Sciences
            "jet", # Journal of Economic Theory
            "jasss", # The Journal of Artificial Societies and Social Simulation
            "ijitdm", # International Journal of Information Technology and Decision Making
            "dga", # Dynamic Games and Applications
            "scw", # Social Choice and Welfare
            # Educational Technology
            "ce", # Computers & Education
            "eait", # Education and Information Technologies
            "bjet", # British Journal of Educational Technology
            "ijwltt", # International Journal of Instruction
            "ile", # Interactive Learning Environments
            "ijet", # International Journal of Emerging Technologies in Learning
            "jcal", # Journal of Computer Assisted Learning
            # Human Computer Interaction
            "pacmhci", # Proceedings of the ACM on Human-Computer Interaction
            "imwut", # Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies
            "taffco", # IEEE Transactions on Affective Computing
            "ijmms", # International Journal of Human-Computer Studies
            "behaviourIT", # Behaviour & Information Technology
            "ijhci", # International Journal of Human-Computer Interaction
            "vr", # Virtual Reality
            "ijim", # International Journal of Interactive Mobile Technologies
            # Evolution Computation
            "asc", # Applied Soft Computing
            "soco", # Soft Computing
            "swevo", # Swarm and Evolutionary Computation
            "evi", # Evolutionary Intelligence
            # Robotics
            "ral", # Robotics: Science and Systems Conference
            "scirobotics", # Science Robotics
            "trob", # IEEE Transactions on Robotics
            # Miscellanious
            "dgov", # Digital Government: Research and Practice
            "dtrap", # Digital Threats: Research and Practice
            "health", # ACM Transactions on Computing for Healthcare
            "jdiq", # Journal of Data and Information Quality
            "taas", # ACM Transactions on Autonomous and Adaptive Systems
            "tops", # ACM Transactions on Privacy and Security
            "tsc", # ACM Transactions on Social Computing
            ]

venues = [
            "ACMdis", # Designing Interactive Systems Conference
         ]

def get_links(venue, year):
    journal = False
    if venue in journals:
        journal = True
        if venue in ["colingjour", "tifsjour"]:
            venue = venue[:-4]
    else:
        if venue in ["colingconf", "tifsconf"]:
            venue = venue[:-4]

    if journal:
        main_url = f"https://dblp.org/db/journals/{venue}/index.html"
    else:
        main_url = f"https://dblp.org/db/conf/{venue}/index.html"
    
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    if journal:
        parts = soup.find("div", id="info-section").find_next_siblings("ul")[0]
        parts = parts.find_all("li")
        for part in  parts:
            if str(year) in part.get_text():
                for month in part.find_all("a"):
                    links.append(month['href'])
    else:
        if venue == "colingconf":
            venue = "coling"
        parts = soup.find_all("cite", itemprop="headline")
        for part in parts:
            if str(year) in part.find("span", class_="title").get_text():
                links.append(part.find("a", class_="toc-link")['href'])
    return links

def crawl_info(url):
    # Send a GET request to the URL
    response = requests.get(url)
    conf = "conf" in url
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <p> tags
        titles = []
        authorss = []
        if conf:
            pubs = soup.find_all('li',class_='entry inproceedings')
        else:
            pubs = soup.find_all('cite',class_='data tts-content')
        for pub in pubs:
            title = pub.find('span', class_='title').text.strip()[:-1]
            authors = pub.find_all('span', itemprop='author')
            authors = ', '.join([author.text.strip() for author in authors])
            titles.append(title)
            authorss.append(authors)
        return titles, authorss
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)

for venue in venues:
    assert venue in confs or venue in journals
    for year in years:
        print('*'*50)
        print(f"Crawl {venue.upper()} {year}")
        links = get_links(venue, year)
        if len(links) == 0:
            continue
        titles = []
        authorss = []
        for link in tqdm(links):
            title, authors = crawl_info(link)
            titles += title
            authorss += authors
        pd.DataFrame({"title":titles, "authors":authorss}).to_csv(f'{venue}{year}_full.csv', index=False)