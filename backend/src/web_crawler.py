# imports
import requests
import re
import nltk
import keybert
import threading
from langdetect import detect
from time import sleep
from urllib.parse import urljoin
from urllib.parse import urlparse, parse_qs
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from datetime import datetime
import threading
from translate import Translator as TranslateTranslator
from googletrans import Translator as GoogleTranslator
# import goslate

# Create a thread-local instance of WordNet and a lock
wordnet_lock = threading.Lock()
db_lock = threading.Lock()
translation_lock = threading.Lock()
kw_model = keybert.KeyBERT()
# Define a thread subclass for crawling URLs


class CrawlThread(threading.Thread):
    """
        CrawlThread function description:
        This class represents a thread that is responsible for crawling a specific URL using the provided crawler.

        Parameters:
        - crawler: An instance of the Crawler class.
        - url: The URL to be crawled.

        Returns:
        - None
        """

    def __init__(self, crawler, url):
        """
        __init__ function description:
        Initializes a CrawlThread instance.

        Parameters:
        - crawler: An instance of the Crawler class.
        - url: The URL to be crawled.

        Returns:
        - None
        """
        super().__init__()
        self.crawler = crawler
        self.url = url

    def run(self):
        """
        run function description:
        Executes the crawling process for the provided URL using the associated Crawler.

        Parameters:
        - None

        Returns:
        - None
        """

        self.crawler.crawl_url(self.url)


class Crawler:

    initial_frontier = [
        "https://dailyperfectmoment.blogspot.com/2014/03/friday-food-favourite-places-cafe.html",
        "https://www.ssc-tuebingen.de/",
        "https://www.tageselternverein.de/",
        "https://www.wila-tuebingen.de/",
        "https://1map.com/maps/germany/tuebingen-38719/",
        "https://allevents.in/tubingen/food-drinks/",
        "https://aris-kommt.de/",
        "https://bestplacesnthings.com/places-to-visit-tubingen-baden-wurttemberg-germany/",
        "https://bolt.eu/de-de/cities/tubingen/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/foodsharing-tuebingen/",
        "https://civis.eu/de/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/en/about-civis/universities/eberhard-karls-universitat-tubingen/",
        "https://crepes-tuebingen.de/",
        "https://cyber-valley.de/",
        "https://edeka-schoeck.de/filiale-tuebingen-berliner-ring/",
        "https://elsa-tuebingen.de/",
        "https://feinschmeckerle.de/2018/05/12/food-rebellen-stilwild-tuebingen/",
        "https://finanzamt-bw.fv-bwl.de/fa_tuebingen/",
        "https://firmeneintrag.creditreform.de/72072/7270059882/HORST_WIZEMANN_FIRE_FOOD_AND_ENTERTAINMENT/",
        "https://food-festivals.com/suche/TÃ¼bingen/",
        "https://foodwissen.de/kuechenstudio-tuebingen/",
        "https://fragdenstaat.de/anfrage/kontrollbericht-zu-asien-food-bazar-tubingen/",
        "https://freistil.beer/category/food-rebellen/",
        "https://geburtshaus-tuebingen.de/",
        "https://genussart.club/food/",
        "https://gym-tue.seminare-bw.de/,Lde/Startseite/Bereiche+_+Faecher/Sport/",
        "https://hc-tuebingen.de/",
        "https://historicgermany.travel/historic-germany/tubingen/",
        "https://hoelderlinturm.de/",
        "https://jgr-tuebingen.de/",
        "https://jobcenter-tuebingen.de/",
        "https://justinpluslauren.com/things-to-do-in-tubingen-germany/",
        "https://karriere-im-sportmanagement.de/hochschulen/universitaet-tuebingen/",
        "https://katholisch-tue.de/",
        "https://kreisbau.com/",
        "https://kunsthalle-tuebingen.de/",
        "https://lebensphasenhaus.de/",
        "https://llpa.kultus-bw.de/,Lde/beim+Regierungspraesidium+Tuebingen/",
        "https://lous-foodtruck.de/foodtruck-tuebingen-2/",
        "https://mapet.de/",
        "https://meine-kunsthandwerker-termine.de/de/veranstaltung/street-food-festival-tuebingen_23109852/",
        "https://mezeakademie.com/",
        "https://mph.tuebingen.mpg.de/",
        "https://mrw-tuebingen.de/",
        "https://nachbarskind.de/",
        "https://naturfreunde-tuebingen.de/",
        "https://netzwerk-onkoaktiv.de/institut/universitaetsklinikum-abteilung-sportmedizin-der-universitaetsklinik-tuebingen/",
        "https://nikolauslauf-tuebingen.de/start/",
        "https://onlinestreet.de/271761-sportkreis-tuebingen-e-v-/",
        "https://ov-tuebingen.thw.de/",
        "https://rds-tue.ibs-bw.de/opac/",
        "https://rp.baden-wuerttemberg.de/rpt/abt7/fachberater/seiten/sport/",
        "https://samphat-thai.de/",
        "https://solawi-tuebingen.de/",
        "https://sport-nachgedacht.de/videobeitrag/ifs-der-uni-tuebingen/",
        "https://sportraepple-shop.de/sportwissenschaft-tuebingen/",
        "https://sports-nut.de/",
        "https://staatsanwaltschaft-tuebingen.justiz-bw.de/pb/,Lde/Startseite/",
        "https://studiengaenge.zeit.de/studium/gesellschaftswissenschaften/sport/sport/standorte/baden-wuerttemberg/tuebingen/",
        "https://studieren.de/sport-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-408.html",
        "https://sv03-tuebingen.de/",
        "https://taz.de/Verpackungssteuer-in-Tuebingen/!5936857/",
        "https://theculturetrip.com/europe/germany/articles/the-best-things-to-see-and-do-in-tubingen-germany/",
        "https://tigers-tuebingen.de/",
        "https://tue.schulamt-bw.de/Startseite/",
        "https://tuebilicious.mewi-projekte.de/2021/06/06/supportyourlocals/",
        "https://tuebingen.ai/",
        "https://tuebingen.city-map.de/01100001/ofterdingen-steinlachtal/online-shops/food/",
        "https://tuebingen.dlrg.de/",
        "https://tuebingen.wlv-sport.de/home/",
        "https://tuebingenresearchcampus.com/",
        "https://tunewsinternational.com/2021/07/08/diesen-samstag-spas-sport-am-samstag-in-tubingen/",
        "https://tv-rottenburg.de/sportangebote/leichtathletik/details-leichtathletik/news/leichtathletik-5-kindersportfest-in-tuebingen/",
        "https://tvstaufia.de/artikel/sport-und-kulturevent-in-tuebingen/",
        "https://unser-tuebingen.de/veranstaltung/street-food-festival-tuebingen-2023/",
        "https://uro-tuebingen.de/",
        "https://wanderlog.com/list/geoCategory/199488/where-to-eat-best-restaurants-in-tubingen/",
        "https://wilhelmsstift.de/",
        "https://www.abfall-kreis-tuebingen.de/",
        "https://www.agentur-fuer-klimaschutz.de/",
        "https://www.altenhilfe-tuebingen.de/",
        "https://www.antenne1.de/",
        "https://www.antiquitaeten-tuebingen.de/",
        "https://www.arbeitsagentur.de/vor-ort/reutlingen/tuebingen/",
        "https://www.atlasobscura.com/things-to-do/tubingen-germany/",
        "https://www.baeckerei-gehr.de/",
        "https://www.bahnhof.de/en/tuebingen-hbf/",
        "https://www.bayer-kastner.de/",
        "https://www.bg-kliniken.de/klinik-tuebingen/",
        "https://www.biwakschachtel-tuebingen.de/",
        "https://www.blutspendezentrale.de/",
        "https://www.bongoroots.de/",
        "https://www.booking.com/attractions/city/de/tubingen.de.html",
        "https://www.boxenstop-tuebingen.de/",
        "https://www.brillinger.de/",
        "https://www.burgermeister-cafegino.de/",
        "https://www.bwegt.de/land-und-leute/das-land-erleben/veranstaltungen/detail/streetfood-festival-tuebingen/schummeltag-street-food-festival/37abfd6f-5ba4-407e-8274-e06f99b4cdc7/",
        "https://www.bwva.de/",
        "https://www.cegat.de/",
        "https://www.cht.com/",
        "https://www.cloudno7.de/en/frontpage/",
        "https://www.curevac.com/",
        "https://www.cvjm-tuebingen.de/",
        "https://www.dai-tuebingen.de/",
        "https://www.dav-tuebingen.de/",
        "https://www.demografie-portal.de/DE/Politik/Baden-Wuerttemberg/Sport/interview-christine-vollmer-tuebingen.html",
        "https://www.dentalbauer.de/",
        "https://www.die-food-trucks.de/nach-stadt/tubingen/",
        "https://www.diegutelaune.de/",
        "https://www.discovergermany.com/university-town-tubingen/",
        "https://www.dr-droescher.de/",
        "https://www.drk-tuebingen.de/",
        "https://www.dzif.de/de/standorte/tuebingen/",
        "https://www.easy-sports.com/",
        "https://www.eml-unitue.de/",
        "https://www.esg-tuebingen.de/",
        "https://www.europeanbestdestinations.com/destinations/tubingen/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/",
        "https://www.eventbrite.com/d/germany--t%C3%BCbingen/events--today/",
        "https://www.evstift.de/",
        "https://www.expedia.co.uk/Things-To-Do-In-Tuebingen.d181220.Travel-Guide-Activities/",
        "https://www.faros-tuebingen.com/",
        "https://www.faz.net/aktuell/feuilleton/thema/tuebingen/",
        "https://www.feuerwehr-tuebingen.de/",
        "https://www.fliesen-kemmler.de/",
        "https://www.foodtruck-mieten24.de/food-truck-mieten-in-tuebingen/",
        "https://www.gastroguide.de/city/tuebingen/schnell-mal-was-essen/",
        "https://www.gea.de/",
        "https://www.germanfoodblogs.de/interviews/2019/6/12/jan-aus-tbingen-esszettel/",
        "https://www.germansights.com/tubingen/",
        "https://www.geschichtswerkstatt-tuebingen.de/",
        "https://www.gesundheit-studieren.com/",
        "https://www.gruene-tuebingen.de/home/",
        "https://www.gss-tuebingen.de/",
        "https://www.gwg-tuebingen.de/",
        "https://www.haertha.de/",
        "https://www.hgv-tuebingen.de/",
        "https://www.hih-tuebingen.de/",
        "https://www.hochschulregion.de/",
        "https://www.hornbach.de/mein-markt/baumarkt-hornbach-tuebingen/",
        "https://www.hospiz-tuebingen.de/",
        "https://www.hubnspoke.de/",
        "https://www.ibyteburgers.com/",
        "https://www.ibyteburgers.com/standorte-kalender/",
        "https://www.immatics.com/",
        "https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/",
        "https://www.institutfrancais.de/",
        "https://www.intersport.de/haendlersuche/sportgeschaefte-baden-wuerttemberg/72072-tuebingen-intersport-raepple/",
        "https://www.itdesign.de/",
        "https://www.jacques.de/depot/44/tuebingen/",
        "https://www.japengo.eu/",
        "https://www.karg-und-petersen.de/",
        "https://www.kaufda.de/Filialen/Tuebingen/Fast-Food/v-c24/",
        "https://www.keb-tuebingen.de/",
        "https://www.keeptravel.com/germany/attraction/ozero-anlagen/",
        "https://www.kern-medical.com/",
        "https://www.kirchenmusikhochschule.de/",
        "https://www.kohenoor-tuebingen.de/",
        "https://www.kreis-tuebingen.de/Startseite.html",
        "https://www.ksk-tuebingen.de/",
        "https://www.kulturnetz-tuebingen.de/",
        "https://www.kupferblau.de/2020/12/18/die-besten-take-away-geheimtipps-in-tuebingen/",
        "https://www.landestheater-tuebingen.de/",
        "https://www.lebenshilfe-tuebingen.de/",
        "https://www.littleindia-tuebingen.de/",
        "https://www.lpb-tuebingen.de/",
        "https://www.mcshape.com/",
        "https://www.medizin.uni-tuebingen.de/",
        "https://www.medsports.de/",
        "https://www.mehrrettich.de/",
        "https://www.mein-check-in.de/tuebingen/overview/",
        "https://www.meinprospekt.de/tuebingen/filialen/fast-food/",
        "https://www.meteoblue.com/de/wetter/woche/TÃ¼bingen_deutschland_2820860/",
        "https://www.mey-generalbau-triathlon.com/",
        "https://www.mhp-pflege.de/",
        "https://www.minube.net/what-to-see/germany/baden-wurttemberg/tubingen/",
        "https://www.miomente.de/stuttgart/kulinarische-stadtfuehrung-tuebingen-meet-und-eat-tuebingen/",
        "https://www.mode-zinser.de/",
        "https://www.museumsgesellschaft-tuebingen.de/",
        "https://www.my-stuwe.de/",
        "https://www.mygermanyvacation.com/best-things-to-do-and-see-in-tubingen-germany/",
        "https://www.nabu-tuebingen.de/",
        "https://www.nc-werte.info/hochschule/uni-tuebingen/sport-sportpublizistik/",
        "https://www.ndr.de/sport/Sieg-gegen-Tuebingen-Rostock-Seawolves-auf-Titelkurs,seawolves886.html",
        "https://www.neckarcamping.de/",
        "https://www.neue-verpackung.de/food/verwaltungsgerichtshof-kippt-verpackungssteuer-in-tuebingen-225.html",
        "https://www.northdata.de/TS+Food+GmbH,+TÃ¼bingen/Amtsgericht+Stuttgart+HRB+748766/",
        "https://www.nuna-store.com/",
        "https://www.nusser-schaal.de/",
        "https://www.occ-tuebingen.de/",
        "https://www.outdooractive.com/en/places-to-see/tuebingen/landscape-in-tuebingen/21876965/",
        "https://www.ovesco.com/",
        "https://www.pagina.gmbh/",
        "https://www.phorn.de/",
        "https://www.pinterest.com/pin/424956914818546372/",
        "https://www.post-sv-tuebingen.de/",
        "https://www.praeventionssport-tuebingen.de/",
        "https://www.profamilia.de/angebote-vor-ort/baden-wuerttemberg/tuebingen/",
        "https://www.raktuebingen.de/",
        "https://www.reddit.com/r/Tuebingen/comments/12ghnvz/best_place_to_grab_food_to_go/",
        "https://www.reservix.de/sport-in-tuebingen/",
        "https://www.rrsct.de/",
        "https://www.rsg-tuebingen.de/",
        "https://www.rskv-tuebingen.de/",
        "https://www.sam-regional.de/de/magazinbeitraege-gastronomie/1/140/slow-food/",
        "https://www.schmaelzle.de/",
        "https://www.shs-capital.eu/",
        "https://www.sit-sis.de/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/",
        "https://www.sluurpy.de/",
        "https://www.sozialforum-tuebingen.de/",
        "https://www.speicher-tuebingen.de/",
        "https://www.spiegel.de/wirtschaft/service/tuebingen-plant-steuer-auf-fast-food-verpackungen-a-834b811e-1a28-4f4f-b8c3-ec4dd20659e2/",
        "https://www.sport-studieren.de/hochschulen/universitaet-tuebingen/",
        "https://www.sport2000.de/stores/tuebingen/",
        "https://www.sportfechter.de/",
        "https://www.sportkreis-tuebingen.de/",
        "https://www.sportwelten.de/TSG-TUeBINGEN_1/",
        "https://www.srg-tuebingen.de/",
        "https://www.stadtseniorenrat-tuebingen.de/",
        "https://www.stern.de/politik/deutschland/themen/tuebingen-4161038.html",
        "https://www.stiftskirche-tuebingen.de/",
        "https://www.storymaker.de/",
        "https://www.streetquizine.de/",
        "https://www.studieren-studium.com/studium/studieren/Sport-TÃ¼bingen/",
        "https://www.studis-online.de/studium/sport-sportwissenschaften/uni-tuebingen-23883/",
        "https://www.stura-tuebingen.de/",
        "https://www.sudhaus-tuebingen.de/",
        "https://www.sueddeutsche.de/thema/TÃ¼bingen/",
        "https://www.suedweststrom.de/",
        "https://www.superfoodz-store.com/",
        "https://www.swtue.de/",
        "https://www.tagblatt.de/",
        "https://www.tagesschau.de/inland/tuebingen-verpackungssteuer-100.html",
        "https://www.team-training.de/",
        "https://www.teamplan.de/",
        "https://www.thehotelguru.com/en-eu/best-hotels-in/germany/tubingen/",
        "https://www.tierschutzverein-tuebingen.de/",
        "https://www.tif-tuebingen.de/",
        "https://www.tourism-bw.com/attractions/museum-der-universitaet-tuebingen-mut-alte-kulturen-52732dcb08/",
        "https://www.travelocity.com/Things-To-Do-In-Tuebingen.d181220.Travel-Guide-Activities/",
        "https://www.trip.com/travel-guide/tubingen-44519/tourist-attractions/",
        "https://www.tropenklinik.de/",
        "https://www.tsg-tuebingen.de/",
        "https://www.tsv-lustnau.de/",
        "https://www.ttc-tuebingen.de/",
        "https://www.tue-kiss.de/",
        "https://www.tuebingen-info.de/",
        "https://www.tuebingen.de/",
        "https://www.tuebinger-erbe-lauf.de/",
        "https://www.tuemarkt.de/",
        "https://www.tvderendingen.de/",
        "https://www.udo-tuebingen.de/",
        "https://www.ukt-physio.de/spezielle-therapie/sportphysiotherapie/",
        "https://www.uni-tuebingen.de/",
        "https://www.unterwegsunddaheim.de/2022/08/tuebingen-sehenswuerdigkeiten-in-der-universitaetsstadt-am-neckar/#:~:text=TÃ¼bingen%20ist%20eine%20der,h%C3%BCbsche%20Altstadt%20direkt%20am%20Neckarufer./",
        "https://www.verifort-capital.de/",
        "https://www.vermoegenundbau-bw.de/ueber-uns/standorte/amt-tuebingen/",
        "https://www.vhs-tuebingen.de/kurse/gesundheit/kategorie/Essen+und+Trinken/288/",
        "https://www.viamichelin.com/web/Tourist-Attractions/Tourist-Attractions-Tubingen-72070-Baden_Wurttemberg-Germany/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/",
        "https://www.we-celebrate.de/foodtruck-tuebingen/",
        "https://www.wotif.com/Things-To-Do-In-Tuebingen.d181220.Travel-Guide-Activities/",
        "https://www.wurstkueche.com/en/frontpage-2/",
        "https://www.zar.de/",
        "https://www.zdf.de/politik/laenderspiegel/unterwegs-in-tuebingen-100.html",
        "https://www.zeltwanger.de/",
        "https://xn--yogaloft-tbingen-szb.com/",
        "https://zsl-bw.de/,Lde/Startseite/ueber-das-zsl/regionalstelle-tuebingen/",
    ]

    # our blacklist
    blacklist = [
        'https://www.tripadvisor.com/',
        'https://www.yelp.com/',
        'https://airtable.com/',
        'https://reddit.com/',
        'https://api.whatsapp.com/',
        'https://twitter.com/',
        'https://www.linkedin.com/',
        'https://apps.apple.com/',
        'https://play.google.com/',
        'https://careers.twitter.com/',
        'https://facebook.com/',
        'https://maps.google.com/',
        'https://create.twitter.com/',
        'https://is.mpg.de',
        'https://www.expedia.co.uk',
        'https://www.reservix.de/',
        'https://www.travelocity.com',
        'https://www.wotif.com/',
    ]

    db = None

    def __init__(self, db) -> None:
        """
        __init__ function description:
        Initializes an instance of the Crawler class.

        Parameters:
        - db: The database instance used to store crawled data.

        Returns:
        - None
        """

        self.db = db
        self.user_agent = 'TuebingenExplorer/1.0'
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        self.min_depth_limit = 0
        self.max_depth_limit = 2
        self.max_threads = 12
        self.base_crawl_delay = 2.0
        self.frontier = 2

        # If the frontier is empty, we load it with our initial frontier
        if self.frontier == 0:
            if self.db.check_frontier_empty():
                for link in self.initial_frontier:
                    self.db.push_to_frontier(link)

        elif self.frontier == 1:
            if self.db.check_frontier_empty1():
                for link in self.initial_frontier:
                    self.db.push_to_frontier1(link)

        elif self.frontier == 2:
            if self.db.check_frontier_empty2():
                for link in self.initial_frontier:
                    self.db.push_to_frontier2(link)

    # Helper Functions

    def crawl_url(self, url):
        """
        crawl_url function description:
        Crawls a web page and extracts relevant information.

        Parameters:
        - url (str): The URL of the web page to crawl.
        - visited_urls (list): A list of visited URLs.
        - id (int): The web page ID starting with 0

        Returns:
        - None
        """

        print(f'LETS GO: {url}')

        # Code to measure the execution time
        if urljoin(url, '/') not in self.blacklist:
            # Make an HTTP GET request to the URL
            try:
                response = requests.get(url)
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                full_host = (
                    f"{parsed_url.scheme}://{host}"
                    if f"{parsed_url.scheme}://{host}".endswith('/')
                    else f"{parsed_url.scheme}://{host}/"
                )
            except:
                print(f"No request possible {url}")
                return  # Exit the function

            if full_host.endswith('.html/'):
                full_host = full_host[:-1]

            # Check if the request is successful (status code 200)
            if response.status_code == 200:
                # Check if crawling is allowed and if a delay is set
                allowed_delay = is_crawling_allowed(
                    self.base_crawl_delay, url, self.user_agent
                )
                allowed = allowed_delay[0]
                crawl_delay = (
                    allowed_delay[1] if allowed_delay[1] else self.base_crawl_delay
                )
                if allowed:
                    # Use BeautifulSoup to parse the HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # get the sitemap for the host from the sitemap table
                    sitemap = get_sitemap_from_host(self, full_host)
                    domain_external_links = []

                    try:
                        internal_links = []
                        external_links = []

                        links = get_internal_external_links(
                            soup,
                            sitemap,
                            domain_external_links,
                            full_host,
                            url,
                            self,
                        )

                        internal_links = links[0]
                        external_links = links[1]
                        sitemap = links[2]
                        domain_external_links = links[3]
                    except Exception as e:
                        print(
                            f"Exception occurred while intern extern : {url} | {e}")

                    set_sitemap_to_host(self, full_host, sitemap)

                    add_external_link_to_sitemap(self, domain_external_links)

                    if not has_tuebingen_content(url):
                        print(f"Not a Tübingen page: exiting {url}")
                        return  # Exit the function

                    index = None
                    title = ""
                    title = get_page_title(soup)

                    normalized_title = ""
                    normalized_title = normalize_text(title) if title else None

                    description = ""
                    description = get_description(soup)

                    normalized_description = ""
                    normalized_description = (
                        normalize_text(description) if description else None
                    )

                    content = get_page_content(soup)
                    normalized_content = normalize_text(
                        content) if content else None
                    limited_content = ""
                    limited_content = limit_string_to_50_words(
                        content)

                    try:
                        keywords = get_keywords(
                            normalized_content, normalized_title, normalized_description
                        )
                    except Exception as e:
                        print(
                            f"Exception occurred while keywords: {url} | {e}")

                    in_links = []

                    out_links = []

                    img = list(get_image_url(soup, url))

                    # Create the web page object
                    web_page = create_web_page_object(
                        id,
                        url,
                        index,
                        title,
                        normalized_title,
                        keywords,
                        description,
                        normalized_description,
                        internal_links,
                        external_links,
                        in_links,
                        out_links,
                        limited_content,
                        normalized_content,
                        img,
                    )

                    # Save to the database
                    with db_lock:
                        try:
                            entry = self.db.add_document(web_page)
                            # If the document is in the db already, we get None back
                            web_page['id'] = None if entry is None else entry[0]
                        except Exception as e:
                            print(
                                f"Exception occurred while adding document: {url} | {e}\n"
                            )

                    with db_lock:
                        try:
                            # Add the URL to the visited URLs list
                            if entry is not None:
                                self.db.add_visited_url(web_page['id'], url)
                        except Exception as e:
                            print(
                                f"Exception occurred while adding visitied: {url} | {e}"
                            )

                    # Delay before crawling the next page
                    sleep(crawl_delay)

                    # else:
                    #     print(f"Not an English page: {url} or doesnt contain Tübingen")
                else:
                    print(f"Error crawling: {url} | Allowed: {allowed} ")
            else:
                print(
                    f"Error crawling: {url} | Status: {response.status_code}")
        else:
            print(f"Domain blacklisted: {urljoin(url, '/')}")

    #  Start crawling all URLs in the frontier
    def crawl(self):
        """
        crawl function description:
        Initiates the crawling process.

        Parameters:
        - None

        Returns:
        - None
        """
        threads = []
        while True:
            with db_lock:
                if self.frontier == 0:
                    next_urls = self.db.get_from_frontier(self.max_threads)
                if self.frontier == 1:
                    next_urls = self.db.get_from_frontier1(self.max_threads)
                if self.frontier == 2:
                    next_urls = self.db.get_from_frontier2(self.max_threads)
                if next_urls is None:
                    break

            for url in next_urls:
                if self.frontier == 0:
                    self.db.remove_from_frontier(url)

                if self.frontier == 1:
                    self.db.remove_from_frontier1(url)

                if self.frontier == 2:
                    self.db.remove_from_frontier2(url)
                thread = CrawlThread(self, url)
                thread.start()
                threads.append(thread)

            # Wait for all remaining threads to complete
            for thread in threads:
                thread.join()

            for thread in threads:
                threads.remove(thread)

    def create_inout_links(self):
        """
        create_inout_links function description:
        Populates the in_links and out_links fields in the database.

        Parameters:
        - None

        Returns:
        - None
        """
        self.db.create_inoutlinks()


def limit_string_to_50_words(input_string):
    """
    limit_string_to_50_words function description:
    Limits the input string to contain only the first 50 words.

    Parameters:
    - input_string (str): The input string to be limited.

    Returns:
    - str: The limited string containing the first 50 words.
    """

    # Split the input string into words
    words = input_string.split()

    # Take the first 50 words
    limited_words = words[:50]

    # Join the words back into a new string
    limited_string = " ".join(limited_words)

    return limited_string


def get_sitemap_from_host(self, domain):
    """
    get_sitemap_from_host function description:
    Gets the sitemap from the given domain.

    Parameters:
    - domain (string): The domain to retrieve the sitemap from.

    Returns:
    - list: The sitemap list of the domain, or an empty list if the host is not found.
    """

    with db_lock:
        try:
            sitemap = list(self.db.get_sitemap_from_domain(domain))
            return sitemap
        except Exception as e:
            print(f"Exception occurred while getting sitemap: {domain} | {e}")
            return []


def set_sitemap_to_host(self, domain, array_to_set):
    """
    set_sitemap_to_host function description:
    Sets the sitemap for the given domain in the database.

    Parameters:
    - domain (string): The domain to update the sitemap for.
    - array_to_set (list): The sitemap list to set for the domain.

    Returns:
    - None
    """

    with db_lock:
        try:
            # update the domain_internal_links
            self.db.update_domain_sitemap(domain, array_to_set)

        except Exception as e:
            print(f"Exception occurred while setting sitemap: {domain} | {e}")


def add_external_link_to_sitemap(self, domain_external_links):
    """
    add_external_link_to_sitemap function description:
    Adds the external links to the sitemap of their respective domains in the database.

    Parameters:
    - domain_external_links (list): A list of external links to be added to the sitemap.

    Returns:
    - None
    """
    # add the external links to the sitemap
    for external in domain_external_links:

        # get domain
        domain = urljoin(external, '/')
        domain = make_pretty_url(domain)

        # prepare link
        external = make_pretty_url(external)

        # call database functions
        # get sitemap
        sitemap = get_sitemap_from_host(self, domain)

        # add this link to the sitemap
        if external not in sitemap:
            sitemap.append(external)
            # write back sitemap
            set_sitemap_to_host(self, domain, sitemap)


def make_pretty_url(link):
    """
    make_pretty_url function description:
    Formats the input URL to have a consistent and pretty representation.

    Parameters:
    - link (str): The input URL to be formatted.

    Returns:
    - str: The formatted URL.
    """
    # prepare link
    if not link.endswith(".html") and not link.endswith(".aspx") and not link.endswith('.pdf'):
        link = (
            link
            if link.endswith("/")
            else link + "/"
        )
    return link


def normalize_german_chars(text):
    """
    Normalizes German characters in a given text to their English equivalents.

    Parameters:
    - text (str): The input text containing German characters.

    Returns:
    - str: The text with normalized German characters.
    """
    replacements = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss'
        # Add more replacements as needed
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def is_text_english(text):
    """
    is_text_english function description:
    Checks if the provided text is in English.

    Parameters:
    - text (str): The input text to be checked.

    Returns:
    - bool: True if the text is in English, False otherwise.
    """
    text = str(text)

    try:
        language_code = detect(text)
        return language_code == 'en'
    except:
        return False


def create_web_page_object(
    id,
    url,
    index,
    title,
    normalized_title,
    keywords,
    description,
    normalized_description,
    internal_links,
    external_links,
    in_links,
    out_links,
    content,
    normalized_content,
    img,
):
    """
    create_web_page_object function description:
    Creates a dictionary representing a web page object with various attributes.

    Parameters:
    - id (int): The web page ID.
    - url (str): The URL of the web page.
    - index (None or int): The index of the web page.
    - title (str): The title of the web page.
    - normalized_title (str): The normalized title of the web page.
    - keywords (list): The list of keywords associated with the web page.
    - description (str): The description of the web page.
    - normalized_description (str): The normalized description of the web page.
    - internal_links (list): The list of internal links on the web page.
    - external_links (list): The list of external links on the web page.
    - in_links (list): The list of incoming links to the web page.
    - out_links (list): The list of outgoing links from the web page.
    - content (str): The content of the web page.
    - normalized_content (str): The normalized content of the web page.
    - img (list): The list of image URLs on the web page.

    Returns:
    - dict: A dictionary representing the web page object with various attributes.
    """

    return {
        'id': 0,
        'url': url,
        'index': index,
        'title': title,
        'normalized_title': normalized_title,
        'keywords': keywords,
        'description': description,
        'normalized_description': normalized_description,
        'internal_links': internal_links,
        'external_links': external_links,
        'in_links': in_links,
        'out_links': out_links,
        'content': content,
        'normalized_content': normalized_content,
        'img': img,
    }


def is_crawling_allowed(base_crawl_delay, url, user_agent):
    """
    Checks if crawling is allowed for the given URL and user agent.

    Parameters:
    - url (str): The URL of the web page.
    - user_agent (str): The user agent string identifying the crawler.

    Returns:
    - (bool): True if crawling is allowed, False otherwise.
    - (float): The crawl delay in seconds if specified, base_crawl_delay otherwise.
    """
    base_url = urljoin(url, '/')
    robots_url = urljoin(base_url, 'robots.txt')

    # Fetch the Robots.txt file
    robot = RobotFileParser()
    robot.set_url(robots_url)
    robot.read()

    # Check if crawling is allowed for the given user agent
    if robot.can_fetch(user_agent, url):
        delay = robot.crawl_delay(user_agent)
        if delay:
            crawl_delay = delay
        else:
            crawl_delay = base_crawl_delay
        return True, crawl_delay
    else:
        return False, base_crawl_delay


def get_page_title(soup):
    """
    get_page_title function description:
    Retrieves the page title from the provided BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.

    Returns:
    - str: The page title if found and in English, otherwise the translated title.
    """
    try:
        title = soup.title.string if soup.title else None

        if title != None and is_text_english(title):
            return soup.title.string if soup.title else None
        else:
            return translate_to_english(title)

    except:
        return ''


def get_keywords(normalized_content, normalized_title, normalized_description):
    """
    Extracts the keywords from the content using the RAKE algorithm.

    Parameters:
    - normalized_content (str): The normalized_content to extract keywords from.
    - normalized_title (str): The normalized_title to extract keywords from.
    - normalized_description (str): The normalized_description to extract keywords from.

    Returns:
    - list: The extracted keywords as a list of single words.
    """

    concat = ""
    if normalized_content is not None:
        concat += normalized_content + " "
    if normalized_title is not None:
        concat += normalized_title
    if normalized_description is not None:
        concat += normalized_description

    keywords_a = kw_model.extract_keywords(concat, top_n=20)
    keywords = [normalize_text(key[0]) for key in keywords_a]

    return keywords


def translate_to_english(text):
    """
    translate_to_english function description:
    Translates the provided text from German to English.

    Parameters:
    - text (str): The text to be translated.

    Returns:
    - str: The translated text in English, or an empty string if translation fails.
    """
    with translation_lock:
        try:
            if text is None or not text:
                return ""
            else:
                translator = GoogleTranslator()
                translation = translator.translate(text, src='de', dest='en')
                return translation.text
        except:

            try:
                text = str(text)
                translator = TranslateTranslator(from_lang='de', to_lang='en')
                translation = translator.translate(text)
                return translation
            except:
                return ""


def get_description(soup):
    """
    get_description function description:
    Retrieves the description meta tag from the provided BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.

    Returns:
    - str: The content of the description meta tag if found and in English, otherwise the translated content.
    """
    try:
        description = soup.find('meta', attrs={'name': 'description'})
        if description['content'] != None and is_text_english(description):
            return description['content']
        else:
            return translate_to_english(description['content']) if description['content'] else None
    except:
        return ''


def has_tuebingen_content(url):
    """
    has_tuebingen_content function description:
    Checks if the provided URL contains content related to Tübingen.

    Parameters:
    - url (str): The URL to be checked.

    Returns:
    - bool: True if the URL contains Tübingen-related content, False otherwise.
    """
    user_agent = 'TuebingenExplorer/1.0'
    base_crawl_delay = 2.0
    try:
        response = requests.get(url)

        allowed_delay = is_crawling_allowed(
            base_crawl_delay, url, user_agent)
        allowed = allowed_delay[0]

        if allowed:
            is_allowed = is_crawling_allowed(2.0, url, user_agent)
            if is_allowed[0]:
                # Use BeautifulSoup to parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                words_to_check = ['tuebingen',
                                  'Tuebingen',
                                  'tübingen',
                                  'Tübingen'
                                  ]
                for word in words_to_check:
                    if soup.find(text=lambda text: word in text):
                        return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f"Exception occurred while crawling: {url} | {e}")


def get_internal_external_links(
    soup, domain_internal_links, domain_external_links, host, url, self
):
    """
    get_internal_external_links function description:
    Retrieves internal and external links from the provided BeautifulSoup object and updates the link lists.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.
    - domain_internal_links (list): A list of internal links for the domain.
    - domain_external_links (list): A list of external links for the domain.
    - host (str): The host of the web page.
    - url (str): The URL of the web page.
    - self: The instance of the current class.

    Returns:
    - tuple: A tuple containing the updated internal and external link lists for the domain.
    """
    url = make_pretty_url(url)

    # get the base url
    base_url = host
    internal_links = []
    external_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if (
            href
            and not href.startswith('mailto:')
            and not href.startswith('tel:')
            and not href.startswith('javascript:')
            and not href.endswith('.jpg')
            and not href.endswith('.png')
            and not href.endswith('.gif')
            and not href.endswith('.webp')
            and not href.endswith('.pdf')
            and not href.endswith('.xml')
            and not '@' in href
            and not '?' in href
        ):

            if href.startswith('http'):
                external_link = href

                external_link = external_link if external_link.startswith(
                    'https') else external_link.replace("http://", "https://")

                #! add "/" if missing
                external_link = make_pretty_url(external_link)
                # check if we should push the url to the frontier
                # check if not in blacklist
                # if base_url not in self.blacklist:
                #     # check if depth is fine
                #     depth = calculate_url_depth(external_link)
                #     if depth <= self.max_depth_limit and depth >= self.min_depth_limit:
                #         # check if not in internal array
                #         if external_link != url:

                #             # check if not in sitemap
                #             domain = urljoin(external_link, '/')
                #             domain = make_pretty_url(domain)
                #             sitemap_from_this_host = get_sitemap_from_host(
                #                 self, domain)
                #             if external_link not in sitemap_from_this_host:

                #                 if external_link not in external_links:
                #                     with db_lock:
                #                         # frontier push here
                #                         # print(
                #                         #     f'add external link to frontier: {external_link}'
                #                         # )
                #                         self.db.push_to_frontier(external_link)

                # add all internal links to web_page_property
                external_links.append(external_link)

                # Add the URL to the domain sitemap
                # if not has_tuebingen_content(external_link):
                domain_external_links.append(external_link)

            elif not href.startswith('#') and not '#' in href:
                href = href if href.startswith('/') else '/' + href
                internal_link = base_url[:-1] + href
                #! add "/" if missing
                internal_link = make_pretty_url(internal_link)

                # check if we should push the url to the frontier
                # check if not in blacklist
                if base_url not in self.blacklist:
                    # check if depth is fine
                    depth = calculate_url_depth(internal_link)
                    if depth <= self.max_depth_limit and depth >= self.min_depth_limit:
                        # check if the internal link is the same url
                        if internal_link != url:
                            # check if not in sitemap
                            if internal_link not in domain_internal_links:
                                # if not has_tuebingen_content(internal_link):
                                with db_lock:
                                    # frontier push here
                                    if depth == 0:
                                        self.db.push_to_frontier(
                                            internal_link)

                                    elif depth == 1:
                                        self.db.push_to_frontier1(
                                            internal_link)
                                    else:
                                        self.db.push_to_frontier2(
                                            internal_link)
                # add all internal links to web_page_property
                internal_links.append(internal_link)

                # Add the URL to the domain sitemap
                domain_internal_links.append(internal_link)

    return (
        list(set(internal_links)),
        list(set(external_links)),
        list(set(domain_internal_links)),
        list(set(domain_external_links)),
    )


def calculate_url_depth(url):
    """
    Calculates the depth of a URL based on the number of slashes in the path.
    If the URL contains '/en/' or '/english/' but not at the end, the depth is adjusted.
    https://example.com/ => depth = 0
    https://example.com/en/ => depth = 0
    https://example.com/page/ => depth = 1
    https://example.com/en/page/ => depth = 1

    Parameters:
    - url (str): The URL for which to calculate the depth.

    Returns:
    - int: The depth of the URL.
    """
    # Parse the URL to extract the path
    parsed_url = urlparse(url)
    query = parsed_url.query

    path = parsed_url.path

    # add missing /
    path = path if path.endswith('/') else path + '/'

    # Calculate the depth based on the number of slashes in the path
    depth = path.count("/") - 1

    # Check if the URL contains '/en/' or '/english/' but not at the end
    if "/en/" in path or "/english/" in path:
        depth -= 1

    # Check if the URL has query parameters
    if query:
        depth += 1

        # Check if the query parameters contain a 'year' parameter
        query_params = parse_qs(query)
        year_param = query_params.get('year[]')
        if year_param:
            # Extract the first value of the 'year' parameter
            year = year_param[0]

            # Get the current year
            current_year = datetime.now().year
            # Check if the year is smaller than the current year - 3 years
            if int(year) < current_year - 3:
                return None  # Skip this URL

    return depth


def get_page_content(soup):
    """
    Extracts the plain text content of a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - str: content of the web page.
    """
    # Get the remaining content
    content = str(soup)

    #! lets try our own regex the getText() function returns bullshit
    # Remove script tags and their content
    content = re.sub(r'<script[^>]*>[\s\S]*?<\/script>', ' ', content)

    # Remove style tags and their content
    content = re.sub(r'<style[^>]*>[\s\S]*?<\/style>', ' ', content)

    # Remove nav tags and their content
    content = re.sub(r'<nav[^>]*>[\s\S]*?<\/nav>', ' ', content)

    # Remove footer tags and their content
    content = re.sub(r'<footer[^>]*>[\s\S]*?<\/footer>', ' ', content)

    # Remove HTML comments
    content = re.sub(r'<!--[\s\S]*?-->', ' ', content)

    # Remove HTML tags
    content = re.sub(r'<.*?>', ' ', content)

    # Remove special characters (except "." and "@") and lowercase the content
    content = re.sub(r'[^\w\s.@]', '', content).lower()

    # Split the content into words using spaces as the delimiter
    word_array = content.split()

    # Remove any leading/trailing whitespaces from each word in the array
    word_array = [word.strip() for word in word_array]

    # Remove empty strings from the array
    word_array = list(filter(None, word_array))

    # Join the elements in the array with an empty space in between
    final_string = " ".join(word_array)

    if final_string and not is_text_english(final_string):
        final_string = translate_to_english(final_string)

    return final_string


def get_image_url(soup, url):
    """
    get_image_url function description:
    Retrieves the image URL from the provided BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.
    - url (str): The URL of the web page.

    Returns:
    - list: A list containing the extracted og:image URL and favicon URL.
    """

    # Find the og:twitter image tag
    og_image_tag = soup.find("meta", attrs={"property": "og:image"})

    # Find the og:twitter image tag
    twitter_image_tag = soup.find("meta", attrs={"property": "twitter:imag"})

    # Find the favicon tag
    favicon_tag = soup.find("link", rel="icon")

    # Extract the favicon URL
    if favicon_tag is not None:
        favicon_url = favicon_tag.get("href", "")
        if favicon_url:
            favicon_url = urljoin(url, '/')[:-1] + favicon_url
    else:
        favicon_url = "empty"

    # Extract the og:image image URL
    if og_image_tag is not None:
        og_image_url = og_image_tag.get("content", "")
        if og_image_url:
            og_image_url = og_image_url if og_image_url.startswith(
                'http') else 'https:' + og_image_url

            return [og_image_url, favicon_url]

    # Extract the twitter:image URL
    elif twitter_image_tag is not None:
        og_image_url = twitter_image_tag.get("content", "")
        if og_image_url:
            og_image_url = og_image_url if og_image_url.startswith(
                'http') else urljoin(url, '/')[:-1] + og_image_url

            return [og_image_url, favicon_url]

    return ""


def pos_tagger(tag):
    """
    pos_tagger function description:
    Maps the part-of-speech tag to the appropriate WordNet POS tag.

    Parameters:
    - tag (str): The part-of-speech tag to be mapped.

    Returns:
    - None or str: The WordNet POS tag corresponding to the input tag, or None if the tag is not recognized.
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def normalize_text(input):
    """
    normalize_text function description:
    Normalizes the input text by removing special characters, lowercasing, normalizing German characters to English equivalents, tokenizing, removing stopwords, and lemmatizing.

    Parameters:
    - input (str): The input text to be normalized.

    Returns:
    - str: The normalized text.
    """
    # Remove special characters and lowercase the content
    content = re.sub(r'[^\w\s]', '', input).lower()

    # Normalize German characters to English equivalents
    content = normalize_german_chars(content)

    # Tokenize the content
    tokens = word_tokenize(content)

    with wordnet_lock:
        # Remove stopwords
        stopwords_set = set(stopwords.words('english'))
        filtered_tokens = [
            token for token in tokens if token not in stopwords_set]

        # Get tags on each word
        token_pos_tags = nltk.pos_tag(filtered_tokens)
        wordnet_tag = map(lambda x: (x[0], pos_tagger(x[1])), token_pos_tags)
        lemmatized_content = []

        # Lemmatize the content
        lemmatizer = WordNetLemmatizer()

        for word, tag in wordnet_tag:
            if tag is None:
                lemmatized_content.append(word)
            else:
                lemmatized_content.append(lemmatizer.lemmatize(word, tag))

    # Convert the lemmatized content back to a string
    return ' '.join(lemmatized_content)
