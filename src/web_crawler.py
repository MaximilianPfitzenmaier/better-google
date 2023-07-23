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

    # initial_frontier = [
    #     "https://dailyperfectmoment.blogspot.com/2014/03/friday-food-favourite-places-cafe.html",
    #     "https://www.ssc-tuebingen.de/",
    #     "https://www.tageselternverein.de/",
    #     "https://www.wila-tuebingen.de/",
    #     "https://1map.com/maps/germany/tuebingen-38719/",
    #     "https://allevents.in/tubingen/food-drinks/",
    #     "https://aris-kommt.de/",
    #     "https://bestplacesnthings.com/places-to-visit-tubingen-baden-wurttemberg-germany/",
    #     "https://bolt.eu/de-de/cities/tubingen/",
    #     "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/foodsharing-tuebingen/",
    #     "https://civis.eu/de/activities/civis-openlab/civis-open-lab-tubingen/",
    #     "https://civis.eu/en/about-civis/universities/eberhard-karls-universitat-tubingen/",
    #     "https://crepes-tuebingen.de/",
    #     "https://cyber-valley.de/",
    #     "https://edeka-schoeck.de/filiale-tuebingen-berliner-ring/",
    #     "https://elsa-tuebingen.de/",
    #     "https://feinschmeckerle.de/2018/05/12/food-rebellen-stilwild-tuebingen/",
    #     "https://finanzamt-bw.fv-bwl.de/fa_tuebingen/",
    #     "https://firmeneintrag.creditreform.de/72072/7270059882/HORST_WIZEMANN_FIRE_FOOD_AND_ENTERTAINMENT/",
    #     "https://food-festivals.com/suche/TÃ¼bingen/",
    #     "https://foodwissen.de/kuechenstudio-tuebingen/",
    #     "https://fragdenstaat.de/anfrage/kontrollbericht-zu-asien-food-bazar-tubingen/",
    #     "https://freistil.beer/category/food-rebellen/",
    #     "https://geburtshaus-tuebingen.de/",
    #     "https://genussart.club/food/",
    #     "https://gym-tue.seminare-bw.de/,Lde/Startseite/Bereiche+_+Faecher/Sport/",
    #     "https://hc-tuebingen.de/",
    #     "https://historicgermany.travel/historic-germany/tubingen/",
    #     "https://hoelderlinturm.de/",
    #     "https://jgr-tuebingen.de/",
    #     "https://jobcenter-tuebingen.de/",
    #     "https://justinpluslauren.com/things-to-do-in-tubingen-germany/",
    #     "https://karriere-im-sportmanagement.de/hochschulen/universitaet-tuebingen/",
    #     "https://katholisch-tue.de/",
    #     "https://kreisbau.com/",
    #     "https://kunsthalle-tuebingen.de/",
    #     "https://lebensphasenhaus.de/",
    #     "https://llpa.kultus-bw.de/,Lde/beim+Regierungspraesidium+Tuebingen/",
    #     "https://lous-foodtruck.de/foodtruck-tuebingen-2/",
    #     "https://mapet.de/",
    #     "https://meine-kunsthandwerker-termine.de/de/veranstaltung/street-food-festival-tuebingen_23109852/",
    #     "https://mezeakademie.com/",
    #     "https://mph.tuebingen.mpg.de/",
    #     "https://mrw-tuebingen.de/",
    #     "https://nachbarskind.de/",
    #     "https://naturfreunde-tuebingen.de/",
    #     "https://netzwerk-onkoaktiv.de/institut/universitaetsklinikum-abteilung-sportmedizin-der-universitaetsklinik-tuebingen/",
    #     "https://nikolauslauf-tuebingen.de/start/",
    #     "https://onlinestreet.de/271761-sportkreis-tuebingen-e-v-/",
    #     "https://ov-tuebingen.thw.de/",
    #     "https://rds-tue.ibs-bw.de/opac/",
    #     "https://rp.baden-wuerttemberg.de/rpt/abt7/fachberater/seiten/sport/",
    #     "https://samphat-thai.de/",
    #     "https://solawi-tuebingen.de/",
    #     "https://sport-nachgedacht.de/videobeitrag/ifs-der-uni-tuebingen/",
    #     "https://sportraepple-shop.de/sportwissenschaft-tuebingen/",
    #     "https://sports-nut.de/",
    #     "https://staatsanwaltschaft-tuebingen.justiz-bw.de/pb/,Lde/Startseite/",
    #     "https://studiengaenge.zeit.de/studium/gesellschaftswissenschaften/sport/sport/standorte/baden-wuerttemberg/tuebingen/",
    #     "https://studieren.de/sport-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-408.html",
    #     "https://sv03-tuebingen.de/",
    #     "https://taz.de/Verpackungssteuer-in-Tuebingen/!5936857/",
    #     "https://theculturetrip.com/europe/germany/articles/the-best-things-to-see-and-do-in-tubingen-germany/",
    #     "https://tigers-tuebingen.de/",
    #     "https://tue.schulamt-bw.de/Startseite/",
    #     "https://tuebilicious.mewi-projekte.de/2021/06/06/supportyourlocals/",
    #     "https://tuebingen.ai/",
    #     "https://tuebingen.city-map.de/01100001/ofterdingen-steinlachtal/online-shops/food/",
    #     "https://tuebingen.dlrg.de/",
    #     "https://tuebingen.wlv-sport.de/home/",
    #     "https://tuebingenresearchcampus.com/",
    #     "https://tunewsinternational.com/2021/07/08/diesen-samstag-spas-sport-am-samstag-in-tubingen/",
    #     "https://tv-rottenburg.de/sportangebote/leichtathletik/details-leichtathletik/news/leichtathletik-5-kindersportfest-in-tuebingen/",
    #     "https://tvstaufia.de/artikel/sport-und-kulturevent-in-tuebingen/",
    #     "https://unser-tuebingen.de/veranstaltung/street-food-festival-tuebingen-2023/",
    #     "https://uro-tuebingen.de/",
    #     "https://wanderlog.com/list/geoCategory/199488/where-to-eat-best-restaurants-in-tubingen/",
    #     "https://wilhelmsstift.de/",
    #     "https://www.abfall-kreis-tuebingen.de/",
    #     "https://www.agentur-fuer-klimaschutz.de/",
    #     "https://www.altenhilfe-tuebingen.de/",
    #     "https://www.antenne1.de/",
    #     "https://www.antiquitaeten-tuebingen.de/",
    #     "https://www.arbeitsagentur.de/vor-ort/reutlingen/tuebingen/",
    #     "https://www.atlasobscura.com/things-to-do/tubingen-germany/",
    #     "https://www.baeckerei-gehr.de/",
    #     "https://www.bahnhof.de/en/tuebingen-hbf/",
    #     "https://www.bayer-kastner.de/",
    #     "https://www.bg-kliniken.de/klinik-tuebingen/",
    #     "https://www.biwakschachtel-tuebingen.de/",
    #     "https://www.blutspendezentrale.de/",
    #     "https://www.bongoroots.de/",
    #     "https://www.booking.com/attractions/city/de/tubingen.de.html",
    #     "https://www.boxenstop-tuebingen.de/",
    #     "https://www.brillinger.de/",
    #     "https://www.burgermeister-cafegino.de/",
    #     "https://www.bwegt.de/land-und-leute/das-land-erleben/veranstaltungen/detail/streetfood-festival-tuebingen/schummeltag-street-food-festival/37abfd6f-5ba4-407e-8274-e06f99b4cdc7/",
    #     "https://www.bwva.de/",
    #     "https://www.cegat.de/",
    #     "https://www.cht.com/",
    #     "https://www.cloudno7.de/en/frontpage/",
    #     "https://www.curevac.com/",
    #     "https://www.cvjm-tuebingen.de/",
    #     "https://www.dai-tuebingen.de/",
    #     "https://www.dav-tuebingen.de/",
    #     "https://www.demografie-portal.de/DE/Politik/Baden-Wuerttemberg/Sport/interview-christine-vollmer-tuebingen.html",
    #     "https://www.dentalbauer.de/",
    #     "https://www.die-food-trucks.de/nach-stadt/tubingen/",
    #     "https://www.diegutelaune.de/",
    #     "https://www.discovergermany.com/university-town-tubingen/",
    #     "https://www.dr-droescher.de/",
    #     "https://www.drk-tuebingen.de/",
    #     "https://www.dzif.de/de/standorte/tuebingen/",
    #     "https://www.easy-sports.com/",
    #     "https://www.eml-unitue.de/",
    #     "https://www.esg-tuebingen.de/",
    #     "https://www.europeanbestdestinations.com/destinations/tubingen/",
    #     "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/",
    #     "https://www.eventbrite.com/d/germany--t%C3%BCbingen/events--today/",
    #     "https://www.evstift.de/",
    #     "https://www.expedia.co.uk/Things-To-Do-In-Tuebingen.d181220.Travel-Guide-Activities/",
    #     "https://www.faros-tuebingen.com/",
    #     "https://www.faz.net/aktuell/feuilleton/thema/tuebingen/",
    #     "https://www.feuerwehr-tuebingen.de/",
    #     "https://www.fliesen-kemmler.de/",
    #     "https://www.foodtruck-mieten24.de/food-truck-mieten-in-tuebingen/",
    #     "https://www.gastroguide.de/city/tuebingen/schnell-mal-was-essen/",
    #     "https://www.gea.de/",
    #     "https://www.germanfoodblogs.de/interviews/2019/6/12/jan-aus-tbingen-esszettel/",
    #     "https://www.germansights.com/tubingen/",
    #     "https://www.geschichtswerkstatt-tuebingen.de/",
    #     "https://www.gesundheit-studieren.com/",
    #     "https://www.gruene-tuebingen.de/home/",
    #     "https://www.gss-tuebingen.de/",
    #     "https://www.gwg-tuebingen.de/",
    #     "https://www.haertha.de/",
    #     "https://www.hgv-tuebingen.de/",
    #     "https://www.hih-tuebingen.de/",
    #     "https://www.hochschulregion.de/",
    #     "https://www.hornbach.de/mein-markt/baumarkt-hornbach-tuebingen/",
    #     "https://www.hospiz-tuebingen.de/",
    #     "https://www.hubnspoke.de/",
    #     "https://www.ibyteburgers.com/",
    #     "https://www.ibyteburgers.com/standorte-kalender/",
    #     "https://www.immatics.com/",
    #     "https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/",
    #     "https://www.institutfrancais.de/",
    #     "https://www.intersport.de/haendlersuche/sportgeschaefte-baden-wuerttemberg/72072-tuebingen-intersport-raepple/",
    #     "https://www.itdesign.de/",
    #     "https://www.jacques.de/depot/44/tuebingen/",
    #     "https://www.japengo.eu/",
    #     "https://www.karg-und-petersen.de/",
    #     "https://www.kaufda.de/Filialen/Tuebingen/Fast-Food/v-c24/",
    #     "https://www.keb-tuebingen.de/",
    #     "https://www.keeptravel.com/germany/attraction/ozero-anlagen/",
    #     "https://www.kern-medical.com/",
    #     "https://www.kirchenmusikhochschule.de/",
    #     "https://www.kohenoor-tuebingen.de/",
    #     "https://www.kreis-tuebingen.de/Startseite.html",
    #     "https://www.ksk-tuebingen.de/",
    #     "https://www.kulturnetz-tuebingen.de/",
    #     "https://www.kupferblau.de/2020/12/18/die-besten-take-away-geheimtipps-in-tuebingen/",
    #     "https://www.landestheater-tuebingen.de/",
    #     "https://www.lebenshilfe-tuebingen.de/",
    #     "https://www.littleindia-tuebingen.de/",
    #     "https://www.lpb-tuebingen.de/",
    #     "https://www.mcshape.com/",
    #     "https://www.medizin.uni-tuebingen.de/",
    #     "https://www.medsports.de/",
    #     "https://www.mehrrettich.de/",
    #     "https://www.mein-check-in.de/tuebingen/overview/",
    #     "https://www.meinprospekt.de/tuebingen/filialen/fast-food/",
    #     "https://www.meteoblue.com/de/wetter/woche/TÃ¼bingen_deutschland_2820860/",
    #     "https://www.mey-generalbau-triathlon.com/",
    #     "https://www.mhp-pflege.de/",
    #     "https://www.minube.net/what-to-see/germany/baden-wurttemberg/tubingen/",
    #     "https://www.miomente.de/stuttgart/kulinarische-stadtfuehrung-tuebingen-meet-und-eat-tuebingen/",
    #     "https://www.mode-zinser.de/",
    #     "https://www.museumsgesellschaft-tuebingen.de/",
    #     "https://www.my-stuwe.de/",
    #     "https://www.mygermanyvacation.com/best-things-to-do-and-see-in-tubingen-germany/",
    #     "https://www.nabu-tuebingen.de/",
    #     "https://www.nc-werte.info/hochschule/uni-tuebingen/sport-sportpublizistik/",
    #     "https://www.ndr.de/sport/Sieg-gegen-Tuebingen-Rostock-Seawolves-auf-Titelkurs,seawolves886.html",
    #     "https://www.neckarcamping.de/",
    #     "https://www.neue-verpackung.de/food/verwaltungsgerichtshof-kippt-verpackungssteuer-in-tuebingen-225.html",
    #     "https://www.northdata.de/TS+Food+GmbH,+TÃ¼bingen/Amtsgericht+Stuttgart+HRB+748766/",
    #     "https://www.nuna-store.com/",
    #     "https://www.nusser-schaal.de/",
    #     "https://www.occ-tuebingen.de/",
    #     "https://www.outdooractive.com/en/places-to-see/tuebingen/landscape-in-tuebingen/21876965/",
    #     "https://www.ovesco.com/",
    #     "https://www.pagina.gmbh/",
    #     "https://www.phorn.de/",
    #     "https://www.pinterest.com/pin/424956914818546372/",
    #     "https://www.post-sv-tuebingen.de/",
    #     "https://www.praeventionssport-tuebingen.de/",
    #     "https://www.profamilia.de/angebote-vor-ort/baden-wuerttemberg/tuebingen/",
    #     "https://www.raktuebingen.de/",
    #     "https://www.reddit.com/r/Tuebingen/comments/12ghnvz/best_place_to_grab_food_to_go/",
    #     "https://www.reservix.de/sport-in-tuebingen/",
    #     "https://www.rrsct.de/",
    #     "https://www.rsg-tuebingen.de/",
    #     "https://www.rskv-tuebingen.de/",
    #     "https://www.sam-regional.de/de/magazinbeitraege-gastronomie/1/140/slow-food/",
    #     "https://www.schmaelzle.de/",
    #     "https://www.shs-capital.eu/",
    #     "https://www.sit-sis.de/",
    #     "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/",
    #     "https://www.sluurpy.de/",
    #     "https://www.sozialforum-tuebingen.de/",
    #     "https://www.speicher-tuebingen.de/",
    #     "https://www.spiegel.de/wirtschaft/service/tuebingen-plant-steuer-auf-fast-food-verpackungen-a-834b811e-1a28-4f4f-b8c3-ec4dd20659e2/",
    #     "https://www.sport-studieren.de/hochschulen/universitaet-tuebingen/",
    #     "https://www.sport2000.de/stores/tuebingen/",
    #     "https://www.sportfechter.de/",
    #     "https://www.sportkreis-tuebingen.de/",
    #     "https://www.sportwelten.de/TSG-TUeBINGEN_1/",
    #     "https://www.srg-tuebingen.de/",
    #     "https://www.stadtseniorenrat-tuebingen.de/",
    #     "https://www.stern.de/politik/deutschland/themen/tuebingen-4161038.html",
    #     "https://www.stiftskirche-tuebingen.de/",
    #     "https://www.storymaker.de/",
    #     "https://www.streetquizine.de/",
    #     "https://www.studieren-studium.com/studium/studieren/Sport-TÃ¼bingen/",
    #     "https://www.studis-online.de/studium/sport-sportwissenschaften/uni-tuebingen-23883/",
    #     "https://www.stura-tuebingen.de/",
    #     "https://www.sudhaus-tuebingen.de/",
    #     "https://www.sueddeutsche.de/thema/TÃ¼bingen/",
    #     "https://www.suedweststrom.de/",
    #     "https://www.superfoodz-store.com/",
    #     "https://www.swtue.de/",
    #     "https://www.tagblatt.de/",
    #     "https://www.tagesschau.de/inland/tuebingen-verpackungssteuer-100.html",
    #     "https://www.team-training.de/",
    #     "https://www.teamplan.de/",
    #     "https://www.thehotelguru.com/en-eu/best-hotels-in/germany/tubingen/",
    #     "https://www.tierschutzverein-tuebingen.de/",
    #     "https://www.tif-tuebingen.de/",
    #     "https://www.tourism-bw.com/attractions/museum-der-universitaet-tuebingen-mut-alte-kulturen-52732dcb08/",
    #     "https://www.travelocity.com/Things-To-Do-In-Tuebingen.d181220.Travel-Guide-Activities/",
    #     "https://www.trip.com/travel-guide/tubingen-44519/tourist-attractions/",
    #     "https://www.tropenklinik.de/",
    #     "https://www.tsg-tuebingen.de/",
    #     "https://www.tsv-lustnau.de/",
    #     "https://www.ttc-tuebingen.de/",
    #     "https://www.tue-kiss.de/",
    #     "https://www.tuebingen-info.de/",
    #     "https://www.tuebingen.de/",
    #     "https://www.tuebinger-erbe-lauf.de/",
    #     "https://www.tuemarkt.de/",
    #     "https://www.tvderendingen.de/",
    #     "https://www.udo-tuebingen.de/",
    #     "https://www.ukt-physio.de/spezielle-therapie/sportphysiotherapie/",
    #     "https://www.uni-tuebingen.de/",
    #     "https://www.unterwegsunddaheim.de/2022/08/tuebingen-sehenswuerdigkeiten-in-der-universitaetsstadt-am-neckar/#:~:text=TÃ¼bingen%20ist%20eine%20der,h%C3%BCbsche%20Altstadt%20direkt%20am%20Neckarufer./",
    #     "https://www.verifort-capital.de/",
    #     "https://www.vermoegenundbau-bw.de/ueber-uns/standorte/amt-tuebingen/",
    #     "https://www.vhs-tuebingen.de/kurse/gesundheit/kategorie/Essen+und+Trinken/288/",
    #     "https://www.viamichelin.com/web/Tourist-Attractions/Tourist-Attractions-Tubingen-72070-Baden_Wurttemberg-Germany/",
    #     "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/",
    #     "https://www.we-celebrate.de/foodtruck-tuebingen/",
    #     "https://www.wotif.com/Things-To-Do-In-Tuebingen.d181220.Travel-Guide-Activities/",
    #     "https://www.wurstkueche.com/en/frontpage-2/",
    #     "https://www.zar.de/",
    #     "https://www.zdf.de/politik/laenderspiegel/unterwegs-in-tuebingen-100.html",
    #     "https://www.zeltwanger.de/",
    #     "https://xn--yogaloft-tbingen-szb.com/",
    #     "https://zsl-bw.de/,Lde/Startseite/ueber-das-zsl/regionalstelle-tuebingen/",
    # ]

    initial_frontier = [
        "https://1map.com/routes/de-tuebingen-38719_to_de-kirchentellinsfurt-217411/",
        "https://1map.com/routes/de-tuebingen-38719_to_de-nagold-46211/",
        "https://1map.com/routes/de-tuebingen-38719_to_de-pfullingen-102133/",
        "https://1map.com/routes/de-tuebingen-38719_to_de-stuttgart/",
        "https://aeneas.ipc.uni-tuebingen.de/b/ale-ms7-mt3-b3j/",
        "https://agbs.kyb.tuebingen.mpg.de/lwk/",
        "https://agbs.kyb.tuebingen.mpg.de/lwk/sections/",
        "https://agora-evaluation.is.tuebingen.mpg.de/",
        "https://aidshilfe-tuebingen-reutlingen.de/",
        "https://al.is.tuebingen.mpg.de/",
        "https://allevents.in/tubingen/",
        "https://allevents.in/tubingen/all/",
        "https://alma.uni-tuebingen.de/",
        "https://alma.uni-tuebingen.de/alma/pages/cs/sys/portal/hisinoneStartPage.faces/",
        "https://alt2.landestheater-tuebingen.de/",
        "https://am.is.tuebingen.mpg.de/",
        "https://am.is.tuebingen.mpg.de/news/best-paper-finalist-at-icra-2018-in-australia/",
        "https://am.is.tuebingen.mpg.de/person/strimpe/",
        "https://am.is.tuebingen.mpg.de/publications/garciacifuentes-ral/",
        "https://am.is.tuebingen.mpg.de/research_groups/intelligent-control-systems-group/",
        "https://amasia-tuebingen.de/",
        "https://ambrosianum-tuebingen.de/",
        "https://app.cituro.com/booking/stadtmuseumtuebingen#step=1/",
        "https://app.cituro.com/booking/stadtmuseumtuebingen/",
        "https://appointment.wi90.uni-tuebingen.de/",
        "https://attac-tuebingen.de/",
        "https://avg.is.tuebingen.mpg.de/",
        "https://avg.is.tuebingen.mpg.de/person/kaschwarz/",
        "https://b12-tuebingen.de/",
        "https://bayer-kastner.de/standort-tuebingen/",
        "https://bestplacesnthings.com/tag/tubingen/",
        "https://bez-tuebingen.dlrg.de/",
        "https://biber3.ub.uni-tuebingen.de/nelol/cgi-bin/neuerw.pl/",
        "https://biber3.ub.uni-tuebingen.de/sigl/sigl-vv.html"
        "https://bilateralnn.is.tuebingen.mpg.de/",
        "https://bueroaktiv-tuebingen.de/",
        "https://bueroaktiv-tuebingen.de/be-boerse/",
        "https://bueroaktiv-tuebingen.de/be-boerse/initiativen-und-verbaende/",
        "https://bueroaktiv-tuebingen.de/be-boerse/stadt-tuebingen/",
        "https://bueroaktiv-tuebingen.de/be-boerse/tuebinger-vereine/",
        "https://bueroaktiv-tuebingen.de/blog/",
        "https://bueroaktiv-tuebingen.de/freiwillige/",
        "https://bueroaktiv-tuebingen.de/freiwillige/10-tipps-fuer-ihr-freiwilliges-engagement/",
        "https://bueroaktiv-tuebingen.de/freiwillige/freiwilligenangebote-in-tuebingen/",
        "https://bueroaktiv-tuebingen.de/freiwillige/freiwilligenboerse/",
        "https://bueroaktiv-tuebingen.de/freiwillige/schwarzes-brett/",
        "https://bueroaktiv-tuebingen.de/freiwillige/taetigkeitsangebote-in-tuebingen/",
        "https://bueroaktiv-tuebingen.de/fur-vereine-und-initiativen/",
        "https://bueroaktiv-tuebingen.de/impressum/",
        "https://bueroaktiv-tuebingen.de/initiativen/",
        "https://bueroaktiv-tuebingen.de/initiativen/angebote-fuer-initiativen/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/foodsharing-tuebingen/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/initiative-mehr-solidaritat-unter-den-medienschaffenden/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/labyrinth-tuebingen/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/lebens-bunt/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/leihladen-tubingen-grundungsinitiative/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/psychiatriekritische-initiative-tubingen/",
        "https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/weltbewusst-konsumkritischer-stadtrundgang/",
        "https://bueroaktiv-tuebingen.de/kontakt/",
        "https://bueroaktiv-tuebingen.de/projekte/",
        "https://bueroaktiv-tuebingen.de/projekte/aktuelle-projekte/",
        "https://bueroaktiv-tuebingen.de/projekte/regelmaessige-veranstaltungen-und-projekte-vorschlag-pauline/",
        "https://bueroaktiv-tuebingen.de/projekte/vergangene-projekte/",
        "https://bueroaktiv-tuebingen.de/projekte/vergangene-projekte/2014-und-2019-tubinger-vereinswegweiser/",
        "https://bueroaktiv-tuebingen.de/projekte/vergangene-projekte/ankommenspatenschaften/",
        "https://bueroaktiv-tuebingen.de/projekte/vergangene-projekte/buergermentor-innenausbildung-2015/",
        "https://bueroaktiv-tuebingen.de/projekte/vergangene-projekte/museumsgarten/",
        "https://bueroaktiv-tuebingen.de/projekte/vergangene-projekte/museumsgarten/veranstaltungen-im-museumsgarten/",
        "https://bueroaktiv-tuebingen.de/projekte/vergangene-projekte/tuebinger-schutzhuetten/",
        "https://bueroaktiv-tuebingen.de/ueber-uns/",
        "https://bueroaktiv-tuebingen.de/ueber-uns/der-verein/",
        "https://bueroaktiv-tuebingen.de/ueber-uns/jobs-praktikum/",
        "https://bueroaktiv-tuebingen.de/ueber-uns/pressearchiv/",
        "https://bueroaktiv-tuebingen.de/ueber-uns/raumvergabe/",
        "https://bueroaktiv-tuebingen.de/ueber-uns/team/",
        "https://bueroaktiv-tuebingen.de/vereine-2/",
        "https://calendly.com/dai-tuebingen/",
        "https://catullus.uni-tuebingen.de/",
        "https://ccc-tuebingen.de/",
        "https://city-map.com/da/branchebog/region-tubingen-de/camping/1/",
        "https://city-map.com/da/branchebog/region-tubingen-de/ungdomsherberge/1/",
        "https://city-map.com/en/business-directory/region-tubingen-de/camping/1/",
        "https://city-map.com/en/business-directory/region-tubingen-de/youth-hostels-2/1/",
        "https://city-map.com/nl/Branche%20overzicht/region-tubingen-de/campings/1/",
        "https://city-map.com/nl/Branche%20overzicht/region-tubingen-de/jeugdherbergen/1/",
        "https://civis.eu/de/uber-civis/universitaten/eberhard-karls-universitat-tubingen/",
        "https://civis.eu/el/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/el/sxetika-me-to-civis/panepisthmia/eberhard-karls-universitat-tubingen/",
        "https://civis.eu/en/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/es/acerca-de-civis/universidades/eberhard-karls-universitat-tubingen/",
        "https://civis.eu/es/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/fr/a-propos-de-civis/universites/eberhard-karls-universitat-tubingen/",
        "https://civis.eu/fr/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/it/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/it/civis/universita/eberhard-karls-universitat-tubingen/",
        "https://civis.eu/ro/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/ro/despre-civis/universit-i/eberhard-karls-universitat-tubingen/",
        "https://civis.eu/sv/activities/civis-openlab/civis-open-lab-tubingen/",
        "https://civis.eu/sv/om-civis/universitet/eberhard-karls-universitat-tubingen/",
        "https://cloud.gss-tuebingen.de/",
        "https://comtec-web.de/tuebingen/Default.aspx"
        "https://crepes-tuebingen.de/",
        "https://crepes-tuebingen.de/catering/",
        "https://crepes-tuebingen.de/creperie/",
        "https://crepes-tuebingen.de/crepes-wagen/",
        "https://crepes-tuebingen.de/event/crepes-bretonnes-im-viertel-vor-egeria-platz-80/",
        "https://crepes-tuebingen.de/event/kein-crepes-bretonnes-im-viertel-vor-egeria-platz-2/",
        "https://crepes-tuebingen.de/event/kein-crepes-bretonnes-im-viertel-vor-egeria-platz/",
        "https://crepes-tuebingen.de/events/",
        "https://crepes-tuebingen.de/impressum/",
        "https://crepes-tuebingen.de/lehrgang/",
        "https://crepes-tuebingen.de/referenzen/",
        "https://crepes-tuebingen.de/team/",
        "https://crepes-tuebingen.de/verleih/",
        "https://dagm.tuebingen.mpg.de/",
        "https://dav-tuebingen.de/",
        "https://de-de.facebook.com/chocolat.tuebingen/",
        "https://de-de.facebook.com/drktuebingen/",
        "https://de-de.facebook.com/elsatuebingen/",
        "https://de-de.facebook.com/gruenetuebingen/",
        "https://de.linkedin.com/company/daituebingen/",
        "https://de.linkedin.com/company/tuebingen-ai/",
        "https://dktk.dkfz.de/en/sites/tuebingen/",
        "https://dktk.dkfz.de/standorte/tuebingen/",
        "https://edeka-schoeck.de/filiale-tuebingen-berliner-ring/",
        "https://ehrenamt.c2c.ngo/tuebingen/",
        "https://ei.is.tuebingen.mpg.de/",
        "https://ei.is.tuebingen.mpg.de/~mhohmann/cv/",
        "https://ei.is.tuebingen.mpg.de/~mhohmann/mynd/",
        "https://ei.is.tuebingen.mpg.de/awards/",
        "https://ei.is.tuebingen.mpg.de/jobs/cambridge-tubingen-phd-fellowships-in-machine-learning/",
        "https://ei.is.tuebingen.mpg.de/people/",
        "https://ei.is.tuebingen.mpg.de/person/bs/",
        "https://ei.is.tuebingen.mpg.de/person/lpavel/",
        "https://ei.is.tuebingen.mpg.de/research/",
        "https://ei.is.tuebingen.mpg.de/research_groups/computational-imaging/",
        "https://ei.is.tuebingen.mpg.de/research_overviews/",
        "https://ein-saal-fuer-tuebingen.de/",
        "https://ekp.dvvbw.de/intelliform/forms/lra-tuebingen/abfallrecht/pool/vpsweb/anfrage-vpsweb/index/",
        "https://ekp.dvvbw.de/intelliform/forms/lra-tuebingen/gaststaettenrecht/pool/vpsweb/anfrage-vpsweb/index/",
        "https://ekp.dvvbw.de/intelliform/forms/lra-tuebingen/gewerberecht/pool/vpsweb/anfrage-vpsweb/index/",
        "https://ekp.dvvbw.de/intelliform/forms/lra-tuebingen/naturschutz/pool/vpsweb/anfrage-vpsweb/index/",
        "https://ekp.dvvbw.de/intelliform/forms/lra-tuebingen/vps/pool/vpsweb/anfrage-vpsweb/index/",
        "https://ekp.dvvbw.de/intelliform/forms/lra-tuebingen/waffensprengstoffrecht/pool/vpsweb/anfrage-vpsweb/index/",
        "https://ekp.dvvbw.de/intelliform/forms/tuebingen/stadt/pool/vpsweb/anfrage-vpsweb/index/",
        "https://ellis.eu/units/tubingen/",
        "https://elsa-tuebingen.de/",
        "https://elsa-tuebingen.de/akademische-aktivitaeten-aa/",
        "https://elsa-tuebingen.de/aktueller-vorstand-2/",
        "https://elsa-tuebingen.de/areas/",
        "https://elsa-tuebingen.de/auslandspraktika-step/",
        "https://elsa-tuebingen.de/beitrittserklaerung-elsa_tuebingen_version_01_04_2020/",
        "https://elsa-tuebingen.de/blog/2021/05/30/1793/",
        "https://elsa-tuebingen.de/blog/2021/05/30/menschenrechtsnewsletter-mai/",
        "https://elsa-tuebingen.de/blog/2022/02/02/2093/",
        "https://elsa-tuebingen.de/blog/2022/02/02/wie-lese-ich-ein-urteil-vortrag-von-prof-huber/",
        "https://elsa-tuebingen.de/blog/2022/02/03/lw-event-mit-voelker-und-partner-am-03-maerz-2022/",
        "https://elsa-tuebingen.de/blog/2022/02/03/vortrag-zu-kryptowaehrungen-und-blockchain-mit-cms-hasche-sigle/",
        "https://elsa-tuebingen.de/blog/2022/02/21/ausschreibung-von-direktoren-posten/",
        "https://elsa-tuebingen.de/blog/author/secgen_tuebingen/",
        "https://elsa-tuebingen.de/blog/category/menschenrechtsnewsletter/",
        "https://elsa-tuebingen.de/blog/category/uncategorized/",
        "https://elsa-tuebingen.de/du-bei-elsa/",
        "https://elsa-tuebingen.de/ehemalige-2/",
        "https://elsa-tuebingen.de/elsa-alumni-deutschland-e-v/",
        "https://elsa-tuebingen.de/elsa-deutschland-e-v-2/",
        "https://elsa-tuebingen.de/elsa-international/",
        "https://elsa-tuebingen.de/elsa-suedwest/",
        "https://elsa-tuebingen.de/geschichte/",
        "https://elsa-tuebingen.de/kontakt/",
        "https://elsa-tuebingen.de/lw-events-2/",
        "https://elsa-tuebingen.de/mitgliedschaft/",
        "https://elsa-tuebingen.de/satzungen/",
        "https://elsa-tuebingen.de/seminare-und-konferenzen/",
        "https://elsa-tuebingen.de/ueber-elsa/",
        "https://elsa-tuebingen.de/ueber-elsa/elsa-deutschland-e-v/",
        "https://elsa-tuebingen.de/ueber-elsa/partner-2/",
        "https://elsa-tuebingen.de/ueber-elsa/regularien/",
        "https://elsa-tuebingen.de/unser-netzwerk/",
        "https://elsa-tuebingen.de/unser-verein/",
        "https://elsa-tuebingen.de/verein/",
        "https://elsa-tuebingen.de/vereinsstruktur/",
        "https://epv-welt.uni-tuebingen.de/",
        "https://epv-welt.uni-tuebingen.de/RestrictedPages/StartSearch.aspx"
        "https://esg-tuebingen.de/",
        "https://esg-tuebingen.de/hochschulgottesdienste/",
        "https://esg-tuebingen.de/in-der-esg-wohnen/",
        "https://falling-walls.com/yes/workshop/from-phd-to-innovator-tubingen-3031-03-2023/apply/",
        "https://fdat.escience.uni-tuebingen.de/portal/#/start/",
        "https://feinschmeckerle.de/2018/05/12/food-rebellen-stilwild-tuebingen/",
        "https://feinschmeckerle.de/category/restaurant-tipps-reutlingen-metzingen-stuttgart/restaurant-tipps-reutlingen-metzingen-tuebingen/",
        "https://filmtage-tuebingen.de/latino/",
        "https://finanzamt-bw.fv-bwl.de/,Lde/Startseite/Ihr+Finanzamt/fa_tuebingen/",
        "https://fit.uni-tuebingen.de/",
        "https://fm.baden-wuerttemberg.de/de/service/media/mid/grundsteinlegung-neubau-cyber-valley-i-in-tuebingen/",
        "https://fnwtuebingen.blogspot.de/",
        "https://forum.tuebingen.de/",
        "https://franzoesische.filmtage-tuebingen.de/",
        "https://freistil-garten-tubingen.resos.com/booking/",
        "https://fridaysforfuturetuebingen.de/schindhaubasistunnel/",
        "https://gaertnerei-kehrer-tuebingen.de/",
        "https://geburtshaus-tuebingen.de/",
        "https://geburtshaus-tuebingen.de/2023/04/26/maximilian-3/",
        "https://geburtshaus-tuebingen.de/2023/05/21/nora/",
        "https://geburtshaus-tuebingen.de/2023/06/17/matti-2/",
        "https://geburtshaus-tuebingen.de/2023/07/14/nolan/",
        "https://geburtshaus-tuebingen.de/2023/07/15/ida-eloise/",
        "https://geburtshaus-tuebingen.de/2023/07/15/juna-sophie/",
        "https://geburtshaus-tuebingen.de/2023/07/17/lars-3/",
        "https://geburtshaus-tuebingen.de/2023/07/19/zaid/",
        "https://geburtshaus-tuebingen.de/akupunktursprechstunde/",
        "https://geburtshaus-tuebingen.de/anfahrt/",
        "https://geburtshaus-tuebingen.de/baby-artgerecht-treffen/",
        "https://geburtshaus-tuebingen.de/babygalerie/",
        "https://geburtshaus-tuebingen.de/babymassage/",
        "https://geburtshaus-tuebingen.de/basis-tage-gewaltfreie-kommunikation/",
        "https://geburtshaus-tuebingen.de/begegnungen-mit-der-eigenen-schwangerschaft-und-geburt/",
        "https://geburtshaus-tuebingen.de/beitritt-flyer/",
        "https://geburtshaus-tuebingen.de/birthpool-ausleihen/",
        "https://geburtshaus-tuebingen.de/buchtipps/",
        "https://geburtshaus-tuebingen.de/datenschutzerklaerung-2/",
        "https://geburtshaus-tuebingen.de/eltern-coaching/",
        "https://geburtshaus-tuebingen.de/elterntraining/",
        "https://geburtshaus-tuebingen.de/eroeffnungsfest/",
        "https://geburtshaus-tuebingen.de/formulare-fuer-die-geburt/",
        "https://geburtshaus-tuebingen.de/frauen-yoga/",
        "https://geburtshaus-tuebingen.de/geburtshausfuehrung-video/",
        "https://geburtshaus-tuebingen.de/geburtshausgeburt/",
        "https://geburtshaus-tuebingen.de/geburtsvorbereitungskurs-am-vormittag-mit-einem-partnerabend-2/",
        "https://geburtshaus-tuebingen.de/geburtsvorbereitungskurs-am-wochenende/",
        "https://geburtshaus-tuebingen.de/geburtsvorbereitungskurs-im-sommer-mit-2-partnertagen/",
        "https://geburtshaus-tuebingen.de/geburtsvorbereitungskurs-mit-2-partnerabenden/",
        "https://geburtshaus-tuebingen.de/geburtsvorbereitungskurs-mit-partnersamstag/",
        "https://geburtshaus-tuebingen.de/hausgeburt/",
        "https://geburtshaus-tuebingen.de/hebammenvorsorge-video/",
        "https://geburtshaus-tuebingen.de/herbstfest-2016/",
        "https://geburtshaus-tuebingen.de/herbstfest-2017/",
        "https://geburtshaus-tuebingen.de/herbstfest-2018/",
        "https://geburtshaus-tuebingen.de/herbstfest-2019-3/",
        "https://geburtshaus-tuebingen.de/herbstfest-2019/",
        "https://geburtshaus-tuebingen.de/hypnobirthing-kompaktkurs/",
        "https://geburtshaus-tuebingen.de/impressum/",
        "https://geburtshaus-tuebingen.de/interesse-am-geburtshaus/",
        "https://geburtshaus-tuebingen.de/kinderwunschbegleitung/",
        "https://geburtshaus-tuebingen.de/koerpertherapie/",
        "https://geburtshaus-tuebingen.de/kontaktformulare/",
        "https://geburtshaus-tuebingen.de/kosten/",
        "https://geburtshaus-tuebingen.de/mama-baby-yoga/",
        "https://geburtshaus-tuebingen.de/massage/",
        "https://geburtshaus-tuebingen.de/neuer-kursraum/",
        "https://geburtshaus-tuebingen.de/newsletter/",
        "https://geburtshaus-tuebingen.de/notfall-abc-kindernotfallkurse/",
        "https://geburtshaus-tuebingen.de/paar-coaching/",
        "https://geburtshaus-tuebingen.de/philosophie/",
        "https://geburtshaus-tuebingen.de/radiointerview/",
        "https://geburtshaus-tuebingen.de/raeumlichkeiten/",
        "https://geburtshaus-tuebingen.de/rtf-1-nachrichten/",
        "https://geburtshaus-tuebingen.de/rueckbildungskrabbeln/",
        "https://geburtshaus-tuebingen.de/rueckbildungskurs-fuer-verwaiste-muetter/",
        "https://geburtshaus-tuebingen.de/rueckbildungskurs/",
        "https://geburtshaus-tuebingen.de/rueckblick-2017/",
        "https://geburtshaus-tuebingen.de/rueckblick-2018/",
        "https://geburtshaus-tuebingen.de/rueckblick/",
        "https://geburtshaus-tuebingen.de/saeuglingspflege/",
        "https://geburtshaus-tuebingen.de/schlafcoaching/",
        "https://geburtshaus-tuebingen.de/schwangeren-yoga/",
        "https://geburtshaus-tuebingen.de/schwangerenbegleitung/",
        "https://geburtshaus-tuebingen.de/sekretariat/",
        "https://geburtshaus-tuebingen.de/sonntagscafe/",
        "https://geburtshaus-tuebingen.de/sprechstunde-fuer-die-zeit-nach-der-geburt/",
        "https://geburtshaus-tuebingen.de/sprechzeiten-kontakt/",
        "https://geburtshaus-tuebingen.de/sternenkinder/",
        "https://geburtshaus-tuebingen.de/stillgruppe/",
        "https://geburtshaus-tuebingen.de/stoffwindel-workshop/",
        "https://geburtshaus-tuebingen.de/story-telling-geburt-wochenbett/",
        "https://geburtshaus-tuebingen.de/strahlend-schoen/",
        "https://geburtshaus-tuebingen.de/team-geburtshilfliches-team/",
        "https://geburtshaus-tuebingen.de/team-wochenbett-team/",
        "https://geburtshaus-tuebingen.de/trage-workshop/",
        "https://geburtshaus-tuebingen.de/ueber-das-geburtshaus/",
        "https://geburtshaus-tuebingen.de/vaeterworkshop/",
        "https://geburtshaus-tuebingen.de/verein-geborgen-geboren/",
        "https://geburtshaus-tuebingen.de/videos/",
        "https://geburtshaus-tuebingen.de/wassergeburt/",
        "https://geburtshaus-tuebingen.de/weitere-veranstaltungen/",
        "https://geburtshaus-tuebingen.de/weiterfuehrende-links/",
        "https://geburtshaus-tuebingen.de/wie-wir-arbeiten/",
        "https://geburtshaus-tuebingen.de/wochenbett-video/",
        "https://geburtshaus-tuebingen.de/wochenbettsprechstunde/",
        "https://geburtshaus-tuebingen.de/yoga-zur-geburtsvorbereitung/",
        "https://gitlab.tuebingen.mpg.de/stark/",
        "https://goal.is.tuebingen.mpg.de/",
        "https://grundsatz-kmv-oktober2020.antragsgruen.de/kmv-tuebingen-oktober2020/",
        "https://haertha.de/standorte/tuebingen/",
        "https://hc-tuebingen.de/",
        "https://historicgermany.travel/event/tuebingen-christmas-market/",
        "https://historicgermany.travel/historic-germany/tubingen/page/2/",
        "https://historicgermany.travel/ja/historic-germany/tubingen/",
        "https://historicgermany.travel/zh-hans/historic-germany/tubingen/",
        "https://homepage.uni-tuebingen.de/VASAT/",
        "https://hotel-metropol-garni-tuebingen.hotel-mix.de/",
        "https://b12-tuebingen.de/",
        "https://gaertnerei-kehrer-tuebingen.de/ueber-uns.html"
        "https://gartengestaltung-tuebingen.de/",
        "https://www.augenblick-tuebingen.de/",
        "https://loeffler-tuebingen.haendlerrenault.de/",
        "https://meine-massage-tuebingen.de/",
        "https://speicher-tuebingen.de/",
        "https://www.adc-tuebingen.de/",
        "https://www.aerztehaus-tuebingen.de/",
        "https://www.angiologie-tuebingen.com/",
        "https://www.arztpraxis-tuebingen.de/",
        "https://www.atem-praxis-tuebingen.de/",
        "https://www.augenarzt-tuebingen.de/",
        "https://www.augenarztpraxis-tuebingen.de/",
        "https://www.autoforum-tuebingen.de/",
        "https://www.banzhaf-tuebingen.de/",
        "https://www.dialyse-in-tuebingen.de/",
        "https://www.dr-lux-tuebingen.de/",
        "https://www.drk-tuebingen.de/",
        "https://www.fashioncut-tuebingen.de/",
        "https://www.getraenketuebingen.de/",
        "https://www.goldankauf-tuebingen.de/",
        "https://www.gyntuebingen.de/",
        "https://www.holzland-tuebingen.de/",
        "https://www.kieferchirurgie-tuebingen.de/",
        "https://www.ksk-tuebingen.de/",
        "https://www.kunstwerkstatt-tuebingen.de/",
        "https://www.lamedina-tuebingen.de/",
        "https://www.logopaedietuebingen.de/",
        "https://www.medizin.uni-tuebingen.de/logopaedenschule/",
        "https://www.mlp-tuebingen2.de/",
        "https://www.mokka-in-tuebingen.de/",
        "https://www.opelhaendler.de/autohaus-lindenschmid_tuebingen-lustnau/",
        "https://www.orthopaediepraxis-tuebingen.de/",
        "https://www.paartherapie-tuebingen.com/",
        "https://www.reusch-tuebingen.de/",
        "https://www.schoene-zaehne-tuebingen.de/",
        "https://www.seibold-tuebingen.de/",
        "https://www.tierklinik-tuebingen.de/",
        "https://www.tuebingen-fewo.de/",
        "https://www.tuebingen-stuckateur.de/",
        "https://www.unfallchirurg-tuebingen.de/",
        "https://www.vinum-tuebingen.de/",
        "https://www.volvocars-partner.de/habfast/tuebingen/",
        "https://www.yoga-vidya-tuebingen.de/",
        "https://www.zahnspange-tuebingen.com/",
        "https://www.safran-tuebingen.de/",
        "https://humangenetik-tuebingen.de/",
        "https://idb.ub.uni-tuebingen.de/digitue/altori/",
        "https://idb.ub.uni-tuebingen.de/digitue/krimdok/",
        "https://idb.ub.uni-tuebingen.de/digitue/regio/",
        "https://idb.ub.uni-tuebingen.de/digitue/southasia/",
        "https://idb.ub.uni-tuebingen.de/digitue/theo/",
        "https://idb.ub.uni-tuebingen.de/digitue/tue/",
        "https://idb.ub.uni-tuebingen.de/digitue/vd18/",
        "https://idb.ub.uni-tuebingen.de/opendigi/Mh824/",
        "https://immo.swp.de/mieten/tuebingen/",
        "https://imprs.tuebingen.mpg.de/]/",
        "https://imprs.tuebingen.mpg.de/de/about-our-imprs.html"
        "https://instagram.com/mrw_tuebingen/",
        "https://instagram.com/nikolauslauf_tuebingen/",
        "https://instagram.com/st.michael.tuebingen/",
        "https://intranet.ub.uni-tuebingen.de/",
        "https://ipac.ub.uni-tuebingen.de/",
        "https://is.mpg.de/en/serviceGroup#tuebingen-it/",
        "https://is.mpg.de/service-group#tuebingen-it/",
        "https://is.tuebingen.mpg.de/employees/yhuang2/",
        "https://is.tuebingen.mpg.de/jobs/",
        "https://is.tuebingen.mpg.de/news/koppen-award-2015-for-dr-jakob-zscheischler/",
        "https://is.tuebingen.mpg.de/person/black/",
        "https://is.tuebingen.mpg.de/publications/2012apjs-201-18m/",
        "https://is.tuebingen.mpg.de/publications/2014apjs-215-8p/",
        "https://is.tuebingen.mpg.de/publications/2016a-a-586a-119s/",
        "https://jazutuebingen.de/",
        "https://jgr-tuebingen.de/",
        "https://jgr-tuebingen.de/antraege-2/",
        "https://jgr-tuebingen.de/author/jgr-intern/",
        "https://jgr-tuebingen.de/category/antraege/",
        "https://jgr-tuebingen.de/category/erfolge/",
        "https://jgr-tuebingen.de/category/ohne-kategorie/",
        "https://jgr-tuebingen.de/category/sitzungen-und-protokolle/",
        "https://jgr-tuebingen.de/category/veranstaltungen/",
        "https://jgr-tuebingen.de/cookie-richtlinie-eu/",
        "https://jgr-tuebingen.de/dachverbandstreffen-in-tuebingen/",
        "https://jgr-tuebingen.de/datenschutz/",
        "https://jgr-tuebingen.de/haushalt-2023/",
        "https://jgr-tuebingen.de/impressum-2/",
        "https://jgr-tuebingen.de/jugendgemeinderaetinnen/",
        "https://jgr-tuebingen.de/letzte-jgr-sitzung-am-14-10/",
        "https://jgr-tuebingen.de/letzte-jgr-sitzung-am-23-9/",
        "https://jgr-tuebingen.de/naechste-jgr-sitzung-am-10-02-2023/",
        "https://jgr-tuebingen.de/naechste-jgr-sitzung-am-17-3/",
        "https://jgr-tuebingen.de/naechste-sitzung-13-01-2022/",
        "https://jgr-tuebingen.de/projektgruppen/",
        "https://jgr-tuebingen.de/schindhaubasistunnel-stoppen/",
        "https://jgr-tuebingen.de/schreib-uns-hier-dein-anliegen/",
        "https://jgr-tuebingen.de/sitzungen/",
        "https://jgr-tuebingen.de/stellungnahmen-neu/",
        "https://jgr-tuebingen.de/wahl-21/",
        "https://jgr-tuebingen.de/wahlrecht-ab-16/",
        "https://jgr-tuebingen.de/wie-funktioniert-der-jgr-2/",
        "https://jgr-tuebingen.de/wp-content/uploads/2021/07/WhatsApp-Image-2021-07-10-at-16.01.17.jpeg/",
        "https://jgr-tuebingen.de/wp-login.php/",
        "https://jgr-tuebingen.de/zusaetzlicher-content-zu-unseren-aktionen/",
        "https://jobcenter-tuebingen.de/",
        "https://jobcenter-tuebingen.de/aktuelles/informationen-zum-thema-ukraine-im-sgb-ii/",
        "https://jobcenter-tuebingen.de/sites/default/files/abschnitt-2022-12/text_abschnitt_1132907244.docx/",
        "https://khg-tuebingen.de/wohnen-und-leben/",
        "https://khg-tuebingen.de/wohnenundleben/khg-esg-stocherkahn/",
        "https://koloniale-orte-tuebingen.de/",
        "https://kreis-tuebingen.de/,Lde/309062.html"
        "https://kreis-tuebingen.de/,Lde/309145.html"
        "https://kreis-tuebingen.de/,Lde/309167.html"
        "https://kreis-tuebingen.de/,Lde/Startseite.html"
        "https://kreisbau.com/aktuelles/50-jahre-landkreis-tuebingen/",
        "https://kreisbau.com/projekte/tubingen-christophstrase-36-38/",
        "https://kunsthalle-tuebingen.de/",
        "https://kunsthalle-tuebingen.de/aktuelle-ausstellung/",
        "https://kunsthalle-tuebingen.de/ausblick/",
        "https://kunsthalle-tuebingen.de/ausser-haus/",
        "https://kunsthalle-tuebingen.de/ausstellungen/daniel-richter/",
        "https://kunsthalle-tuebingen.de/ausstellungen/lunarring/",
        "https://kunsthalle-tuebingen.de/besuch/",
        "https://kunsthalle-tuebingen.de/besuch/cafe-kunsthalle/",
        "https://kunsthalle-tuebingen.de/chronik/",
        "https://kunsthalle-tuebingen.de/datenschutz/",
        "https://kunsthalle-tuebingen.de/en/",
        "https://kunsthalle-tuebingen.de/impressum/",
        "https://kunsthalle-tuebingen.de/kalender/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-21-kunsthalle-60/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-21-yoga-in-der-kunsthalle/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-22-oeffentliche-fuehrung/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-23-kunsthalle-fuer-kids/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-23-oeffentliche-fuehrung/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-25-lets-talk-about-daniel-richter/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-26-kunsthalle-60/",
        "https://kunsthalle-tuebingen.de/kalender/#2023-07-27-oeffentliche-fuehrung/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/fuehrungen-und-workshops-fuer-kindergaerten-und-klassenen/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/fuehrungen/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/jugendliche-und-erwachsene/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/kunsthalle-60-2/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/kunsthalle-fuer-die-ganze-familie/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/kunsthalle-fuer-kids/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/kunsthalle-fuer-unternehmen/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/kunsthalle-inklusiv/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/kunsthalle-open-air/",
        "https://kunsthalle-tuebingen.de/kunst-fuer-alle/speed-dating-mit-der-kunst/",
        "https://kunsthalle-tuebingen.de/kunsthalle-digital/",
        "https://kunsthalle-tuebingen.de/newsletter/",
        "https://kunsthalle-tuebingen.de/presse/",
        "https://kunsthalle-tuebingen.de/ueber-uns/direktorin/",
        "https://kunsthalle-tuebingen.de/ueber-uns/gruendung-und-geschichte-kunsthalle-tuebingen/",
        "https://kunsthalle-tuebingen.de/ueber-uns/konzeption/",
        "https://kunsthalle-tuebingen.de/ueber-uns/kunstvermittlung/",
        "https://kunsthalle-tuebingen.de/ueber-uns/stiftung-kunsthalle-tuebingen/",
        "https://kunsthalle-tuebingen.de/ueber-uns/team/",
        "https://kunsthalle-tuebingen.ticketfritz.de/",
        "https://kunsthalle-tuebingen.ticketfritz.de/Home/Index/",
        "https://kunsthalle-tuebingen.ticketfritz.de/Shop/Detail/50644/35111/",
        "https://kv-tuebingen.antragsgruen.de/",
        "https://kv-tuebingen.drk.de/",
        "https://kvz-tuebingen.drs.de/",
        "https://landestheater-tuebingen.de/artists/view/id/2372/type/inszenierung/Michael_Miensopust.html"
        "https://lav-tuebingen.com/",
        "https://lav-tuebingen.com/mitgliedschaft/",
        "https://lav-tuebingen.com/neu-hier/",
        "https://lists.gruene-tuebingen.de/sympa/subscribe/kv-newsletter/",
        "https://listserv.uni-tuebingen.de/mailman/listinfo/Name_der_Mailingliste/",
        "https://listserv.uni-tuebingen.de/mailman/listinfo/newsletter/",
        "https://lnv-bw.de/lnv-vor-ort/lnv-arbeitskreis-tuebingen/",
        "https://lous-foodtruck.de/foodtruck-tuebingen-2/",
        "https://lpb-tuebingen.de/OB-Wahl-Tue-2022/",
        "https://lpb-tuebingen.de/OB-Wahl-Ulm-2023/",
        "https://mailchi.mp/nikolauslauf-tuebingen/newsletter-12-1/",
        "https://mailchi.mp/nikolauslauf-tuebingen/newsletter-2022-09/",
        "https://mailchi.mp/nikolauslauf-tuebingen/newsletter-2022-10/",
        "https://mailchi.mp/nikolauslauf-tuebingen/newsletter-2022-11/",
        "https://mailchi.mp/nikolauslauf-tuebingen/newsletter-2022-12-2/",
        "https://mailhost.tuebingen.mpg.de/",
        "https://mapet.de/kursplan-tuebingen/",
        "https://mapet.de/training-mapet-rottenburg-tuebingen/",
        "https://mapet.de/tuebingen/",
        "https://meine-kunsthandwerker-termine.de/de/veranstaltung/street-food-festival-tuebingen_23109852/",
        "https://micro-europa.de/queer-durch-tuebingen-aus-dem-archiv-ins-rampenlicht/",
        "https://mlss.tuebingen.mpg.de/2020/",
        "https://mml.cs.uni-tuebingen.de/",
        "https://mml.inf.uni-tuebingen.de/",
        "https://moodle.zdv.uni-tuebingen.de/",
        "https://mover.is.tuebingen.mpg.de/",
        "https://mph.tuebingen.mpg.de/",
        "https://mph.tuebingen.mpg.de/en/",
        "https://mrw-tuebingen.de/",
        "https://mrw-tuebingen.de/aktuelle-menschenrechtswoche/",
        "https://mrw-tuebingen.de/aktuelles/",
        "https://mrw-tuebingen.de/allgemeine-geschaeftsbediungungen/",
        "https://mrw-tuebingen.de/allgemeine-geschaeftsbediungungen/#1618809043710-f4156ba4-0c7e/",
        "https://mrw-tuebingen.de/author/geerte-mrw/",
        "https://mrw-tuebingen.de/author/melanie-mrw/",
        "https://mrw-tuebingen.de/author/sophie-mrw/",
        "https://mrw-tuebingen.de/cookie-richtlinie-eu/",
        "https://mrw-tuebingen.de/danke-2/",
        "https://mrw-tuebingen.de/die-menschenrechtswoche-2023-findet-vom-18-06-bis-zum-25-06-2023-statt/",
        "https://mrw-tuebingen.de/grusswort-von-schirmherrin-gilda-sahebi-zur-menschenrechtswoche-2023/",
        "https://mrw-tuebingen.de/haftungsausschluss/",
        "https://mrw-tuebingen.de/impressum/",
        "https://mrw-tuebingen.de/initiativen/",
        "https://mrw-tuebingen.de/initiativen/#login/",
        "https://mrw-tuebingen.de/initiativen/initiativenpanel/initiativeninfos/",
        "https://mrw-tuebingen.de/login/",
        "https://mrw-tuebingen.de/menschenrechtswoche-2022-rueckblick/",
        "https://mrw-tuebingen.de/mr-preis/",
        "https://mrw-tuebingen.de/mr-preis/jury/",
        "https://mrw-tuebingen.de/organisationsteam/",
        "https://mrw-tuebingen.de/presseinformation/",
        "https://mrw-tuebingen.de/tuebinger-menschenrechtswoche/",
        "https://mrw-tuebingen.de/ueber-uns/",
        "https://mrw-tuebingen.de/ueber-uns/kontakt/",
        "https://mrw-tuebingen.de/vergangene-mrw/",
        "https://mrw-tuebingen.de/woche-allgemein/",
        "https://mrw-tuebingen.de/woche-w/",
        "https://mwk.baden-wuerttemberg.de/de/service/presse-und-oeffentlichkeitsarbeit/pressemitteilung/pid/knapp-20-millionen-fuer-kompetenzzentrum-im-cyber-valley-in-tuebingen/",
        "https://mwk.baden-wuerttemberg.de/de/service/presse-und-oeffentlichkeitsarbeit/pressemitteilung/pid/weg-frei-fuer-cyber-valley-campus-investition-in-standort-tuebingen-von-bis-zu-180-millionen-euro/",
        "https://mwk.baden-wuerttemberg.de/de/service/presse/pressemitteilung/pid/europaweit-erstes-ellis-institut-geht-in-tuebingen-an-den-start/",
        "https://naturfreunde-tuebingen.de/",
        "https://naturfreunde-tuebingen.de/aktivitaeten/",
        "https://naturfreunde-tuebingen.de/aktivitaeten/aktivitaeten-vergangene-jahren/",
        "https://naturfreunde-tuebingen.de/aktivitaeten/aktuelles-programm/",
        "https://naturfreunde-tuebingen.de/aktivitaeten/anmeldung-aktivitaet/",
        "https://naturfreunde-tuebingen.de/aktuelles/",
        "https://naturfreunde-tuebingen.de/calendar/",
        "https://naturfreunde-tuebingen.de/calendar/action~oneday/exact_date~23-7-2023/",
        "https://naturfreunde-tuebingen.de/die-geschichte-der-tuebinger-naturfreunde/",
        "https://naturfreunde-tuebingen.de/familienwanderung-raupen-und-schmetterlinge/",
        "https://naturfreunde-tuebingen.de/links-kontakt/",
        "https://naturfreunde-tuebingen.de/links-kontakt/anfahrt/",
        "https://naturfreunde-tuebingen.de/links-kontakt/datenschutzerklaerung/",
        "https://naturfreunde-tuebingen.de/links-kontakt/impressum/",
        "https://naturfreunde-tuebingen.de/links-kontakt/kontakt/",
        "https://naturfreunde-tuebingen.de/links-kontakt/links/",
        "https://naturfreunde-tuebingen.de/links-kontakt/newsletter/",
        "https://naturfreunde-tuebingen.de/mitglied-werden/",
        "https://naturfreunde-tuebingen.de/nacht-der-nachaltigkeit/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/bezirks-nf-haus-rohrauer-huette/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/geschichte-der-naturfreunde/die-anfaenge-der-og-tuebingen/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/geschichte-der-naturfreunde/die-jahre-1974-1979/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/geschichte-der-naturfreunde/die-zeit-1980-bis-2000/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/geschichte-der-naturfreunde/geschichte-der-naturfreunde/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/geschichte-der-naturfreunde/geschichte-der-tuebinger-naturfreunde-tabellarisch/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/geschichte-der-naturfreunde/von-2001-bis-2008/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/geschichte-der-naturfreunde/von-2009-bis-2014/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/gruppen-der-og/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/naturfreunde-international/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/unsere-ausschuss/",
        "https://naturfreunde-tuebingen.de/og-tuebingen/vereinsheim-neuhalde/",
        "https://naturfreunde-tuebingen.de/rueckblick/",
        "https://naturfreunde-tuebingen.de/sonntagstreff-mit-tag-der-offenen-tuer/",
        "https://naturfreunde-tuebingen.de/vortrag-wildbienen-kennen-foerdern-und-schuetzen/",
        "https://naturfreunde-tuebingen.de/wanderung-von-tuebingen-zum-albvereinsheim-in-pfrondorf/",
        "https://naturfreunde-tuebingen.de/wp-content/gallery/2018-arbeitseinsatz/IMG_20180324_103638_copy.jpeg/",
        "https://naturfreunde-tuebingen.de/wp-content/gallery/bezirkswanderung-2015/bezirkswanderung4.JPG/",
        "https://nhkita.tuebingen.de/anmeldung.html"
        "https://nikolauslauf-tuebingen.de/",
        "https://nikolauslauf-tuebingen.de/31-baden-wuerttembergischer-forstsportlauf-2022/",
        "https://nikolauslauf-tuebingen.de/agb/",
        "https://nikolauslauf-tuebingen.de/aktuelles/",
        "https://nikolauslauf-tuebingen.de/aktuelles/page/2/",
        "https://nikolauslauf-tuebingen.de/aktuelles/page/3/",
        "https://nikolauslauf-tuebingen.de/aktuelles/page/8/",
        "https://nikolauslauf-tuebingen.de/ankuendigung-2022/",
        "https://nikolauslauf-tuebingen.de/anwohner/",
        "https://nikolauslauf-tuebingen.de/archiv/",
        "https://nikolauslauf-tuebingen.de/aufruf-musikgruppen-laufstrecke/",
        "https://nikolauslauf-tuebingen.de/ausschreibung/",
        "https://nikolauslauf-tuebingen.de/ausschreibung/#aenderungen_ummeldungen_abmeldungen/",
        "https://nikolauslauf-tuebingen.de/author/fabian-knisel/",
        "https://nikolauslauf-tuebingen.de/bericht-probelauf-2022/",
        "https://nikolauslauf-tuebingen.de/datenschutz/",
        "https://nikolauslauf-tuebingen.de/datenschutz/#newsletter/",
        "https://nikolauslauf-tuebingen.de/datenschutz/#shariff/",
        "https://nikolauslauf-tuebingen.de/downloads/",
        "https://nikolauslauf-tuebingen.de/ergebnisse/",
        "https://nikolauslauf-tuebingen.de/fotoservice/",
        "https://nikolauslauf-tuebingen.de/frankfurt-marathon-coenning-beste-deutsche/",
        "https://nikolauslauf-tuebingen.de/halbmarathon-ausgebucht-2022/",
        "https://nikolauslauf-tuebingen.de/imagefilm/",
        "https://nikolauslauf-tuebingen.de/impressum/",
        "https://nikolauslauf-tuebingen.de/kollektion/",
        "https://nikolauslauf-tuebingen.de/kontakt/",
        "https://nikolauslauf-tuebingen.de/larasch-eventvideo-2022/",
        "https://nikolauslauf-tuebingen.de/medienecho-2022/",
        "https://nikolauslauf-tuebingen.de/messe/",
        "https://nikolauslauf-tuebingen.de/mithelfen-beim-itdesign-nikolauslauf/",
        "https://nikolauslauf-tuebingen.de/newsletter-2022-09/",
        "https://nikolauslauf-tuebingen.de/newsletter-2022-10/",
        "https://nikolauslauf-tuebingen.de/newsletter-2022-11/",
        "https://nikolauslauf-tuebingen.de/newsletter-2022-12-1/",
        "https://nikolauslauf-tuebingen.de/newsletter-2022-12-2/",
        "https://nikolauslauf-tuebingen.de/newsletter/",
        "https://nikolauslauf-tuebingen.de/originalstrecke/",
        "https://nikolauslauf-tuebingen.de/originalstrecke/#anfahrt/",
        "https://nikolauslauf-tuebingen.de/pm-anmeldestart-2022/",
        "https://nikolauslauf-tuebingen.de/presse/",
        "https://nikolauslauf-tuebingen.de/probelauf/",
        "https://nikolauslauf-tuebingen.de/relativwertung/",
        "https://nikolauslauf-tuebingen.de/schulprojekt-2022/",
        "https://nikolauslauf-tuebingen.de/social-wall/",
        "https://nikolauslauf-tuebingen.de/sozialpartner/",
        "https://nikolauslauf-tuebingen.de/sozialprojekt-2021-spende-schwimmverein/",
        "https://nikolauslauf-tuebingen.de/sozialprojekt-2022-spende-inklusionsfussball/",
        "https://nikolauslauf-tuebingen.de/sponsoren/",
        "https://nikolauslauf-tuebingen.de/starterliste/",
        "https://nikolauslauf-tuebingen.de/tag-des-laufens-2023/",
        "https://nikolauslauf-tuebingen.de/tausch/",
        "https://nikolauslauf-tuebingen.de/training/",
        "https://nikolauslauf-tuebingen.de/training/#gesundheit/",
        "https://nikolauslauf-tuebingen.de/ueber-uns/",
        "https://nikolauslauf-tuebingen.de/wer-macht-was/",
        "https://onlinestreet.de/orte/tuebingen/",
        "https://open-journals.uni-tuebingen.de/index.html"
        "https://open-journals.uni-tuebingen.de/ojs/",
        "https://ovidius.uni-tuebingen.de/",
        "https://ovidius.uni-tuebingen.de/ilias3/",
        "https://owncloud.tuebingen.mpg.de/index.php/s/Jn7QX4jMAF98SJ8/",
        "https://owncloud.tuebingen.mpg.de/index.php/s/LHPfog6pYjsPB5s/",
        "https://owncloud.tuebingen.mpg.de/index.php/s/n9RGyBT5qgfH2FN/",
        "https://owncloud.tuebingen.mpg.de/index.php/s/NGJNK9Smyq23CZc/",
        "https://people.kyb.tuebingen.mpg.de/suvrit/",
        "https://people.kyb.tuebingen.mpg.de/tschultz/",
        "https://people.kyb.tuebingen.mpg.de/tschultz/index.html#CV/",
        "https://people.kyb.tuebingen.mpg.de/tschultz/index.html#Publications/",
        "https://people.kyb.tuebingen.mpg.de/tschultz/index.html#Research/",
        "https://people.tuebingen.mpg.de/bs/alumni.htm/",
        "https://people.tuebingen.mpg.de/bs/biosketch_2023.txt/",
        "https://people.tuebingen.mpg.de/bs/DSC01581.jpeg/",
        "https://people.tuebingen.mpg.de/bs/K2-18b.html"
        "https://people.tuebingen.mpg.de/bs/Milky_Way_Roque_DSC00336.JPG/",
        "https://people.tuebingen.mpg.de/causal-learning/",
        "https://people.tuebingen.mpg.de/felixwidmaier/trifinger/",
        "https://people.tuebingen.mpg.de/harmeling/",
        "https://people.tuebingen.mpg.de/networks-workshop/",
        "https://people.tuebingen.mpg.de/p/causality-perspect/",
        "https://people.tuebingen.mpg.de/stark/campus2.mobileconfig/",
        "https://pn.is.tuebingen.mpg.de/",
        "https://portal.mlcloud.uni-tuebingen.de/",
        "https://post-sv-tuebingen.de/",
        "https://post-sv-tuebingen.de/index.php/datenschutz/",
        "https://post-sv-tuebingen.de/index.php/impressum/",
        "https://post-sv-tuebingen.de/index.php/post-sv-swim-run-projekt/1223-2-swim-run-03-07-2022/",
        "https://post-sv-tuebingen.de/index.php/was-wann-wo-sportabzeichen/",
        "https://ps.is.tuebingen.mpg.de/",
        "https://ps.is.tuebingen.mpg.de/news/michael-j-black-awarded-major-test-of-time-prize-at-the-2020-conference-on-computer-vision-and-pattern-recognition-cvpr/",
        "https://ps.is.tuebingen.mpg.de/person/achandrasekaran/",
        "https://ps.is.tuebingen.mpg.de/person/black/",
        "https://ps.is.tuebingen.mpg.de/person/chuang2/",
        "https://ps.is.tuebingen.mpg.de/person/dcudeiro/",
        "https://ps.is.tuebingen.mpg.de/person/dhoffmann/",
        "https://ps.is.tuebingen.mpg.de/person/dtzionas/",
        "https://ps.is.tuebingen.mpg.de/person/ebonetto/",
        "https://ps.is.tuebingen.mpg.de/person/eprice/",
        "https://ps.is.tuebingen.mpg.de/person/Forte/",
        "https://ps.is.tuebingen.mpg.de/person/gpons/",
        "https://ps.is.tuebingen.mpg.de/person/hacet/",
        "https://ps.is.tuebingen.mpg.de/person/imartinovic/",
        "https://ps.is.tuebingen.mpg.de/person/jyang/",
        "https://ps.is.tuebingen.mpg.de/person/lmueller2/",
        "https://ps.is.tuebingen.mpg.de/person/mhassan/",
        "https://ps.is.tuebingen.mpg.de/person/mkeller2/",
        "https://ps.is.tuebingen.mpg.de/person/mkocabas/",
        "https://ps.is.tuebingen.mpg.de/person/nathanasiou/",
        "https://ps.is.tuebingen.mpg.de/person/nchen/",
        "https://ps.is.tuebingen.mpg.de/person/nowfalali/",
        "https://ps.is.tuebingen.mpg.de/person/nrueegg/",
        "https://ps.is.tuebingen.mpg.de/person/otaheri/",
        "https://ps.is.tuebingen.mpg.de/person/pghosh/",
        "https://ps.is.tuebingen.mpg.de/person/rdanecek/",
        "https://ps.is.tuebingen.mpg.de/person/rludwig/",
        "https://ps.is.tuebingen.mpg.de/person/romero/",
        "https://ps.is.tuebingen.mpg.de/person/sdwivedi/",
        "https://ps.is.tuebingen.mpg.de/person/ssanyal/",
        "https://ps.is.tuebingen.mpg.de/person/stripathi/",
        "https://ps.is.tuebingen.mpg.de/person/szuffi/",
        "https://ps.is.tuebingen.mpg.de/person/vchoutas/",
        "https://ps.is.tuebingen.mpg.de/person/yfeng/",
        "https://ps.is.tuebingen.mpg.de/person/yji/",
        "https://ps.is.tuebingen.mpg.de/person/yliu2/",
        "https://ps.is.tuebingen.mpg.de/person/yxiu/",
        "https://ps.is.tuebingen.mpg.de/publications/aircap2019aerialswarms/",
        "https://ps.is.tuebingen.mpg.de/publications/loper-phd-2017/",
        "https://ps.is.tuebingen.mpg.de/publications/matang-accv-2018/",
        "https://ps.is.tuebingen.mpg.de/publications/mmcorrelation-pami-2018/",
        "https://ps.is.tuebingen.mpg.de/publications/nitin_iccv_19/",
        "https://ps.is.tuebingen.mpg.de/publications/rahul_ral_2019/",
        "https://ps.is.tuebingen.mpg.de/publications/ranjan-thesis/",
        "https://ps.is.tuebingen.mpg.de/publications/sip/",
        "https://ps.is.tuebingen.mpg.de/publications/sun-cvpr-10/",
        "https://ps.is.tuebingen.mpg.de/research_fields/robot-perception-group/",
        "https://ps.is.tuebingen.mpg.de/research_projects/aircaprl/",
        "https://ps.is.tuebingen.mpg.de/research_projects/autonomous-mocap/",
        "https://ps.is.tuebingen.mpg.de/research_projects/facade-segmentation/",
        "https://ps.is.tuebingen.mpg.de/research_projects/semantic-optical-flow/",
        "https://ps.is.tuebingen.mpg.de/talks/capturing-hand-object-interaction-and-reconstruction-of-manipulated-objects/",
        "https://ps.is.tuebingen.mpg.de/uploads_file/attachment/attachment/281/semantic_flow_code_release.zip/",
        "https://publikationen.uni-tuebingen.de/xmlui/",
        "https://publikationen.uni-tuebingen.de/xmlui/handle/10900/42126/",
        "https://rak-tuebingen.de/kontakt/",
        "https://re.is.tuebingen.mpg.de/publications/lieder2019manifesto/",
        "https://reutlingen-tuebingen-nord.rotary.de/",
        "https://reutlingen-tuebingen.rotary.de/",
        "https://riva-tuebingen.de/",
        "https://rp-tuebingen.pageflow.io/biberberater-innen#chapter-2473/",
        "https://rp.baden-wuerttemberg.de/rpt/abt3/ref33/bienenfachberatung-tuebingen/",
        "https://rp.baden-wuerttemberg.de/rpt/presse-und-soziale-medien/pressemitteilungen/artikel/flusspark-neckaraue-tuebingen-nach-ostern-baustart-fuer-den-hochwasserschutz/",
        "https://rp.baden-wuerttemberg.de/rpt/presse-und-soziale-medien/pressemitteilungen/artikel/news-aus-der-tiefe-grundwassersituation-im-regierungsbezirk-tuebingen/",
        "https://sb-tuebingen.lmscloud.net/",
        "https://sb-tuebingen.lmscloud.net/cgi-bin/koha/opac-suggestions.pl/",
        "https://schulamt-tuebingen.de/,Lde/794700/",
        "https://segmentation.is.tuebingen.mpg.de/",
        "https://seminar-tuebingen.de/,Lde/Startseite/",
        "https://server.gss-tuebingen.de/portfolio/aktuelles:mrbs/",
        "https://shapy.is.tuebingen.mpg.de/",
        "https://shg-prostatakrebs-reutlingen-tuebingen.de/",
        "https://shop.apotheke-tuebingen.de/",
        "https://shop.tigers-tuebingen.de/",
        "https://shop.wundmitte.de/shop/category/prasenzseminare-basisseminar-wundexperte-icw-tubingen-32/",
        "https://sitzung.vs-tuebingen.de/agenda/",
        "https://smicv2010.kyb.tuebingen.mpg.de/",
        "https://solawi-tuebingen.de/",
        "https://solawi-tuebingen.de/2018/11/09/hallo-welt/",
        "https://solawi-tuebingen.de/anteile-erwerben/",
        "https://solawi-tuebingen.de/datenschutzerklaerung/",
        "https://solawi-tuebingen.de/fragen-und-antworten/",
        "https://solawi-tuebingen.de/ueber-uns/",
        "https://solawi-tuebingen.de/ueber-uns/biolandhof-baeuerle/",
        "https://solawi-tuebingen.de/ueber-uns/biolandhof-waldhausen/",
        "https://sozialministerium.baden-wuerttemberg.de/de/service/presse/pressemitteilung/pid/land-richtet-kompetenzzentrum-fuer-pflege-und-digitalisierung-in-tuebingen-ein/",
        "https://spenden.twingle.de/evangelische-gesamtkirchengemeinde-tubingen/konto-2008/tw645c9d2623d82/page/",
        "https://sport-nachgedacht.de/videobeitrag/ifs-der-uni-tuebingen/",
        "https://sportdeutschland.tv/tigers-tuebingen/",
        "https://sportkreis-tuebingen.de/kontakt-sk-tuebingen/",
        "https://stm.baden-wuerttemberg.de/de/service/presse/pressemitteilung/pid/vereinbarung-zur-gruendung-eines-ellis-instituts-in-tuebingen-unterzeichnet/",
        "https://stocherkahn.khg-tuebingen.de/",
        "https://stsg-tuebingen.de/",
        "https://studieren.de/accounting-and-finance-eberhard-karls-universitaet-tuebingen.studienprofil.t-0.a-68.c-9715.html"
        "https://studieren.de/aegyptologie-uni-tuebingen.studiengang.t-0.a-68.c-7.html"
        "https://studieren.de/allgemeine-rhetorik-uni-tuebingen.studiengang.t-0.a-68.c-887.html"
        "https://studieren.de/allgemeine-sprachwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-3180.html"
        "https://studieren.de/altorientalische-philologie-uni-tuebingen.studiengang.t-0.a-68.c-1122.html"
        "https://studieren.de/american-studies-uni-tuebingen.studiengang.t-0.a-68.c-1512.html"
        "https://studieren.de/anglistik-amerikanistik-uni-tuebingen.studiengang.t-0.a-68.c-697.html"
        "https://studieren.de/applied-environmental-geoscience-aeg-uni-tuebingen.studiengang.t-0.a-68.c-34642.html"
        "https://studieren.de/betriebswirtschaftslehre-uni-tuebingen.studiengang.t-0.a-68.c-31.html"
        "https://studieren.de/biochemie-uni-tuebingen.studiengang.t-0.a-68.c-35.html"
        "https://studieren.de/biochemistry-uni-tuebingen.studiengang.t-0.a-68.c-35174.html"
        "https://studieren.de/bioinformatik-uni-tuebingen.studiengang.t-0.a-68.c-265.html"
        "https://studieren.de/biologie-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-22701.html"
        "https://studieren.de/biologie-uni-tuebingen.studiengang.t-0.a-68.c-22779.html"
        "https://studieren.de/biomedical-technologies-uni-tuebingen.studiengang.t-0.a-68.c-38077.html"
        "https://studieren.de/chemie-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-22715.html"
        "https://studieren.de/chemie-uni-tuebingen.studiengang.t-0.a-68.c-22778.html"
        "https://studieren.de/comparative-middle-east-politics-and-society-uni-tuebingen.studiengang.t-0.a-68.c-38025.html"
        "https://studieren.de/computerlinguistik-uni-tuebingen.studiengang.t-0.a-68.c-48.html"
        "https://studieren.de/data-science-in-business-and-economics-uni-tuebingen.studienprofil.t-0.a-68.c-43531.html"
        "https://studieren.de/demokratie-und-regieren-in-europa-uni-tuebingen.studiengang.t-0.a-68.c-39728.html"
        "https://studieren.de/deutsch-als-zweitsprache-sprachdiagnostik-und-sprachfoerderung-uni-tuebingen.studiengang.t-0.a-68.c-34643.html"
        "https://studieren.de/deutsch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-474.html"
        "https://studieren.de/deutsche-literatur-uni-tuebingen.studienprofil.t-0.a-68.c-494.html"
        "https://studieren.de/economics-and-business-administration-uni-tuebingen.studienprofil.t-0.a-68.c-9718.html"
        "https://studieren.de/economics-and-finance-eberhard-karls-universitaet-tuebingen.studienprofil.t-0.a-68.c-35544.html"
        "https://studieren.de/economics-uni-tuebingen.studienprofil.t-0.a-68.c-436.html"
        "https://studieren.de/empirische-bildungsforschung-und-paedagogische-psychologie-uni-tuebingen.studiengang.t-0.a-68.c-37100.html"
        "https://studieren.de/empirische-kulturwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-407.html"
        "https://studieren.de/englisch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-846.html"
        "https://studieren.de/english-linguistics-uni-tuebingen.studiengang.t-0.a-68.c-9719.html"
        "https://studieren.de/english-literatures-and-cultures-uni-tuebingen.studiengang.t-0.a-68.c-34073.html"
        "https://studieren.de/erwachsenenbildungweiterbildung-uni-tuebingen.studiengang.t-0.a-68.c-33863.html"
        "https://studieren.de/erziehungswissenschaft-und-soziale-arbeiterwachsenenbildung-uni-tuebingen.studiengang.t-0.a-68.c-43093.html"
        "https://studieren.de/ethnologie-social-and-cultural-anthropology-uni-tuebingen.studiengang.t-0.a-68.c-34644.html"
        "https://studieren.de/ethnologie-uni-tuebingen.studiengang.t-0.a-68.c-2444.html"
        "https://studieren.de/european-economics-eberhard-karls-universitaet-tuebingen.studienprofil.t-0.a-68.c-32796.html"
        "https://studieren.de/european-management-eberhard-karls-universitaet-tuebingen.studienprofil.t-0.a-68.c-64.html"
        "https://studieren.de/evangelische-theologie-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-31835.html"
        "https://studieren.de/forschung-und-entwicklung-in-der-sozialpaedagogiksozialen-arbeit-uni-tuebingen.studiengang.t-0.a-68.c-37101.html"
        "https://studieren.de/franzoesisch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-81.html"
        "https://studieren.de/friedensforschung-und-internationale-politik-uni-tuebingen.studiengang.t-0.a-68.c-1566.html"
        "https://studieren.de/general-management-eberhard-karls-universitaet-tuebingen.studienprofil.t-0.a-68.c-1694.html"
        "https://studieren.de/geographie-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-22718.html"
        "https://studieren.de/geographie-uni-tuebingen.studiengang.t-0.a-68.c-87.html"
        "https://studieren.de/geooekologie-uni-tuebingen.studiengang.t-0.a-68.c-310.html"
        "https://studieren.de/geowissenschaften-uni-tuebingen.studiengang.t-0.a-68.c-315.html"
        "https://studieren.de/germanische-linguistik-theorie-und-empirie-uni-tuebingen.studiengang.t-0.a-68.c-9720.html"
        "https://studieren.de/germanistik-uni-tuebingen.studiengang.t-0.a-68.c-91.html"
        "https://studieren.de/geschichte-international-uni-tuebingen.studiengang.t-0.a-68.c-42471.html"
        "https://studieren.de/geschichte-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-22719.html"
        "https://studieren.de/geschichtswissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-971.html"
        "https://studieren.de/griechisch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-850.html"
        "https://studieren.de/griechisch-uni-tuebingen.studiengang.t-0.a-68.c-32528.html"
        "https://studieren.de/hebammenwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-44318.html"
        "https://studieren.de/humangeographie-global-studies-uni-tuebingen.studiengang.t-0.a-68.c-34234.html"
        "https://studieren.de/humanmedizin-uni-tuebingen.studiengang.t-0.a-68.c-36307.html"
        "https://studieren.de/indologie-south-asian-studies-uni-tuebingen.studiengang.t-0.a-68.c-37738.html"
        "https://studieren.de/informatik-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-22720.html"
        "https://studieren.de/informatik-uni-tuebingen.studiengang.t-0.a-68.c-105.html"
        "https://studieren.de/integrierter-deutschfranzoesischer-studiengang-geschichte-tuebingentuebaix-uni-tuebingen.studiengang.t-0.a-68.c-37362.html"
        "https://studieren.de/interdisciplinary-american-studies-uni-tuebingen.studiengang.t-0.a-68.c-35552.html"
        "https://studieren.de/interkulturelle-deutsch-franzoesische-studien-uni-tuebingen.studiengang.t-0.a-68.c-9725.html"
        "https://studieren.de/international-business-administration-uni-tuebingen.studienprofil.t-0.a-68.c-1040.html"
        "https://studieren.de/international-business-eberhard-karls-universitaet-tuebingen.studienprofil.t-0.a-68.c-110.html"
        "https://studieren.de/international-economics-uni-tuebingen.studienprofil.t-0.a-68.c-1337.html"
        "https://studieren.de/internationale-literaturen-komparatistik-uni-tuebingen.studienprofil.t-0.a-68.c-9727.html"
        "https://studieren.de/islamische-religionslehre-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-39729.html"
        "https://studieren.de/islamische-theologie-im-europaeischen-kontext-uni-tuebingen.studiengang.t-0.a-68.c-39730.html"
        "https://studieren.de/islamische-theologie-uni-tuebingen.studiengang.t-0.a-68.c-6658.html"
        "https://studieren.de/italienisch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-115.html"
        "https://studieren.de/italienisch-uni-tuebingen.studiengang.t-0.a-68.c-33454.html"
        "https://studieren.de/japanologie-uni-tuebingen.studiengang.t-0.a-68.c-116.html"
        "https://studieren.de/japanologiejapanese-studies-uni-tuebingen.studiengang.t-0.a-68.c-39731.html"
        "https://studieren.de/judaistik-uni-tuebingen.studiengang.t-0.a-68.c-499.html"
        "https://studieren.de/katholische-religionslehre-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-853.html"
        "https://studieren.de/katholische-theologie-uni-tuebingen.studiengang.t-0.a-68.c-415.html"
        "https://studieren.de/klassische-archaeologie-uni-tuebingen.studiengang.t-0.a-68.c-628.html"
        "https://studieren.de/kognitionswissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-385.html"
        "https://studieren.de/komparatistik-uni-tuebingen.studiengang.t-0.a-68.c-472.html"
        "https://studieren.de/koreanistik-uni-tuebingen.studiengang.t-0.a-68.c-751.html"
        "https://studieren.de/kunstgeschichte-uni-tuebingen.studiengang.t-0.a-68.c-500.html"
        "https://studieren.de/latein-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-854.html"
        "https://studieren.de/latein-uni-tuebingen.studiengang.t-0.a-68.c-32529.html"
        "https://studieren.de/literatur-und-kulturtheorie-uni-tuebingen.studiengang.t-0.a-68.c-9730.html"
        "https://studieren.de/machine-learning-uni-tuebingen.studiengang.t-0.a-68.c-43558.html"
        "https://studieren.de/management-and-economics-eberhard-karls-universitaet-tuebingen.studienprofil.t-0.a-68.c-6160.html"
        "https://studieren.de/mathematik-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-22724.html"
        "https://studieren.de/mathematik-uni-tuebingen.studiengang.t-0.a-68.c-149.html"
        "https://studieren.de/medieninformatik-uni-tuebingen.studiengang.t-0.a-68.c-332.html"
        "https://studieren.de/medienwissenschaft-en-uni-tuebingen.studiengang.t-0.a-68.c-9731.html"
        "https://studieren.de/medizininformatik-uni-tuebingen.studiengang.t-0.a-68.c-1250.html"
        "https://studieren.de/medizinische-strahlenwissenschaften-medical-radiation-scineces-uni-tuebingen.studiengang.t-0.a-68.c-38078.html"
        "https://studieren.de/medizintechnik-uni-tuebingen.studiengang.t-0.a-68.c-511.html"
        "https://studieren.de/modernes-indien-uni-tuebingen.studiengang.t-0.a-68.c-34647.html"
        "https://studieren.de/molecular-cell-biology-and-immunology-uni-tuebingen.studiengang.t-0.a-68.c-40797.html"
        "https://studieren.de/molekulare-medizin-molecular-medicine-uni-tuebingen.studiengang.t-0.a-68.c-70.html"
        "https://studieren.de/musikwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-162.html"
        "https://studieren.de/nanosciences-uni-tuebingen.studiengang.t-0.a-68.c-37739.html"
        "https://studieren.de/naturwissenschaft-und-technik-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-34648.html"
        "https://studieren.de/naturwissenschaftliche-archaeologie-uni-tuebingen.studiengang.t-0.a-68.c-34649.html"
        "https://studieren.de/neuro-und-verhaltenswissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-37734.html"
        "https://studieren.de/neurobiologie-uni-tuebingen.studiengang.t-0.a-68.c-46417.html"
        "https://studieren.de/neuronale-informationsverarbeitung-uni-tuebingen.studiengang.t-0.a-68.c-37735.html"
        "https://studieren.de/neuroscience-uni-tuebingen.studiengang.t-0.a-68.c-33793.html"
        "https://studieren.de/palaeoanthropologie-uni-tuebingen.studiengang.t-0.a-68.c-37740.html"
        "https://studieren.de/pflege-uni-tuebingen.studiengang.t-0.a-68.c-373.html"
        "https://studieren.de/pharmaceutical-sciences-and-technologies-uni-tuebingen.studiengang.t-0.a-68.c-39732.html"
        "https://studieren.de/pharmazie-uni-tuebingen.studiengang.t-0.a-68.c-171.html"
        "https://studieren.de/philosophie-ethik-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-3368.html"
        "https://studieren.de/philosophie-uni-tuebingen.studiengang.t-0.a-68.c-172.html"
        "https://studieren.de/physik-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-22725.html"
        "https://studieren.de/physik-uni-tuebingen.studiengang.t-0.a-68.c-173.html"
        "https://studieren.de/physische-geographie-landscape-system-science-uni-tuebingen.studiengang.t-0.a-68.c-34652.html"
        "https://studieren.de/politik-und-gesellschaft-ostasiens-uni-tuebingen.studiengang.t-0.a-68.c-9736.html"
        "https://studieren.de/politikwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-174.html"
        "https://studieren.de/politikwissenschaftwirtschaftswissenschaft-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-34475.html"
        "https://studieren.de/populationbased-medicine-uni-tuebingen.studienprofil.t-0.a-68.c-45832.html"
        "https://studieren.de/portugiesisch-uni-tuebingen.studiengang.t-0.a-68.c-176.html"
        "https://studieren.de/psychologie-uni-tuebingen.studiengang.t-0.a-68.c-178.html"
        "https://studieren.de/rechtswissenschaften-uni-tuebingen.studiengang.t-0.a-68.c-2604.html"
        "https://studieren.de/romanische-literaturwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-3299.html"
        "https://studieren.de/romanische-sprachwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-9737.html"
        "https://studieren.de/russisch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-193.html"
        "https://studieren.de/schulforschung-und-schulentwicklung-uni-tuebingen.studiengang.t-0.a-68.c-37102.html"
        "https://studieren.de/schulpsychologie-uni-tuebingen.studiengang.t-0.a-68.c-37741.html"
        "https://studieren.de/sinologie-chinese-studies-mit-beruflichen-schwerpunkt-uni-tuebingen.studiengang.t-0.a-68.c-37737.html"
        "https://studieren.de/sinologie-chinese-studies-uni-tuebingen.studiengang.t-0.a-68.c-37736.html"
        "https://studieren.de/sinologiechinesisch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-39733.html"
        "https://studieren.de/skandinavistik-uni-tuebingen.studiengang.t-0.a-68.c-478.html"
        "https://studieren.de/slavistik-uni-tuebingen.studiengang.t-0.a-68.c-2284.html"
        "https://studieren.de/sozialpaedagogikpaedagogik-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-33942.html"
        "https://studieren.de/soziologie-diversitaet-und-gesellschaft-uni-tuebingen.studiengang.t-0.a-68.c-44116.html"
        "https://studieren.de/soziologie-empirische-sozialforschung-uni-tuebingen.studiengang.t-0.a-68.c-38105.html"
        "https://studieren.de/soziologie-uni-tuebingen.studiengang.t-0.a-68.c-401.html"
        "https://studieren.de/spanisch-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-203.html"
        "https://studieren.de/sport-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-408.filter-10.html"
        "https://studieren.de/sport-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-408.filter-8.html"
        "https://studieren.de/sport-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-408.html"
        "https://studieren.de/sportwissenschaft-uni-tuebingen.studiengang.t-0.a-68.c-205.html"
        "https://studieren.de/sprachen-geschichte-und-kulturen-des-nahen-ostens-uni-tuebingen.studiengang.t-0.a-68.c-9740.html"
        "https://studieren.de/umweltnaturwissenschaften-uni-tuebingen.studiengang.t-0.a-68.c-2461.html"
        "https://studieren.de/uni-tuebingen.hochschule.t-0.a-68.html"
        "https://studieren.de/ur-und-fruehgeschichtliche-archaeologie-und-archaeologie-des-mittelalters-uni-tuebingen.studiengang.t-0.a-68.c-9741.html"
        "https://studieren.de/volkswirtschaftslehre-uni-tuebingen.studiengang.t-0.a-68.c-231.html"
        "https://studieren.de/vorderasiatische-archaeologie-und-palaestinaarchaeologie-uni-tuebingen.studiengang.t-0.a-68.c-37742.html"
        "https://studieren.de/vorderasiatische-archaeologie-uni-tuebingen.studiengang.t-0.a-68.c-646.html"
        "https://studieren.de/vormoderne-uni-tuebingen.studiengang.t-0.a-68.c-37743.html"
        "https://studieren.de/zahnmedizin-uni-tuebingen.studiengang.t-0.a-68.c-245.html"
        "https://studieren.de/zellulaere-und-molekulare-neurowissenschaften-uni-tuebingen.studiengang.t-0.a-68.c-34654.html"
        "https://survey-is.tuebingen.mpg.de/index.php/418582/",
        "https://survey-is.tuebingen.mpg.de/index.php/987167/",
        "https://sv03-tuebingen.de/",
        "https://sv03-tuebingen.de/#/",
        "https://sv03-tuebingen.de/aixenprovence2023/",
        "https://sv03-tuebingen.de/basketball/",
        "https://sv03-tuebingen.de/basketball1/",
        "https://sv03-tuebingen.de/boxen/",
        "https://sv03-tuebingen.de/boxen/haeufige-fragen/",
        "https://sv03-tuebingen.de/boxen/kontakt/",
        "https://sv03-tuebingen.de/boxen/team/",
        "https://sv03-tuebingen.de/boxen/trainingszeiten/",
        "https://sv03-tuebingen.de/boxen/verschiedenes/",
        "https://sv03-tuebingen.de/datenschutz/",
        "https://sv03-tuebingen.de/eltern-kind-turnen/",
        "https://sv03-tuebingen.de/floorball/",
        "https://sv03-tuebingen.de/floorball/aktuelles-berichte/",
        "https://sv03-tuebingen.de/floorball/interesse/",
        "https://sv03-tuebingen.de/floorball/kontakt-abteilungsleitung/",
        "https://sv03-tuebingen.de/floorball/was-ist-floorball/",
        "https://sv03-tuebingen.de/frauenfitness/",
        "https://sv03-tuebingen.de/fussball/",
        "https://sv03-tuebingen.de/fussball/sv-03-stadion/",
        "https://sv03-tuebingen.de/fussballer-zurueck-aus-der-winterpause/",
        "https://sv03-tuebingen.de/handball/",
        "https://sv03-tuebingen.de/hauptverein/",
        "https://sv03-tuebingen.de/impressum/",
        "https://sv03-tuebingen.de/internationales-turnier/",
        "https://sv03-tuebingen.de/klaus-wuest/",
        "https://sv03-tuebingen.de/kontakt/",
        "https://sv03-tuebingen.de/leichtathletik/",
        "https://sv03-tuebingen.de/news/",
        "https://sv03-tuebingen.de/paddelfreunde/",
        "https://sv03-tuebingen.de/paddelfreunde/berichte/",
        "https://sv03-tuebingen.de/paddelfreunde/trainingszeiten/",
        "https://sv03-tuebingen.de/sport-und-floorball-feriencamp-fuer-kinder-6-12-jahre-vom-23-27-august/",
        "https://sv03-tuebingen.de/sportangebote/",
        "https://sv03-tuebingen.de/swt-vorteilskarte/",
        "https://sv03-tuebingen.de/tennis/",
        "https://sv03-tuebingen.de/tischtennis/",
        "https://sv03-tuebingen.de/ultimate-frisbee/",
        "https://team-training.de/kurse/einfach-in-arbeit-%e2%88%92-bewerbung-coaching-und-deutsch-fuer-den-beruf-fuer-frauen-und-maenner-mit-migrationshintergrund-tuebingen/",
        "https://team-training.de/kurse/jobclub-tuebingen-bewerbungsberatung-und-bewerbungsbegleitung/",
        "https://team-training.de/locations/tuebingen/",
        "https://terminreservierung.blutspende.de/spendezentren/tuebingen/termine/",
        "https://tigers-tuebingen.de/",
        "https://tigers-tuebingen.de/2018/05/",
        "https://tigers-tuebingen.de/2018/06/",
        "https://tigers-tuebingen.de/2018/07/",
        "https://tigers-tuebingen.de/2018/08/",
        "https://tigers-tuebingen.de/2018/09/",
        "https://tigers-tuebingen.de/2018/10/",
        "https://tigers-tuebingen.de/2018/11/",
        "https://tigers-tuebingen.de/2018/12/",
        "https://tigers-tuebingen.de/2019/01/",
        "https://tigers-tuebingen.de/2019/02/",
        "https://tigers-tuebingen.de/2019/03/",
        "https://tigers-tuebingen.de/2019/04/",
        "https://tigers-tuebingen.de/2019/05/",
        "https://tigers-tuebingen.de/2019/06/",
        "https://tigers-tuebingen.de/2019/07/",
        "https://tigers-tuebingen.de/2019/08/",
        "https://tigers-tuebingen.de/2019/09/",
        "https://tigers-tuebingen.de/2019/10/",
        "https://tigers-tuebingen.de/2019/11/",
        "https://tigers-tuebingen.de/2019/12/",
        "https://tigers-tuebingen.de/2020/01/",
        "https://tigers-tuebingen.de/2020/02/",
        "https://tigers-tuebingen.de/2020/03/",
        "https://tigers-tuebingen.de/2020/04/",
        "https://tigers-tuebingen.de/2020/05/",
        "https://tigers-tuebingen.de/2020/06/",
        "https://tigers-tuebingen.de/2020/07/",
        "https://tigers-tuebingen.de/2020/08/",
        "https://tigers-tuebingen.de/2020/09/",
        "https://tigers-tuebingen.de/2020/10/",
        "https://tigers-tuebingen.de/2020/11/",
        "https://tigers-tuebingen.de/2020/12/",
        "https://tigers-tuebingen.de/2021/01/",
        "https://tigers-tuebingen.de/2021/02/",
        "https://tigers-tuebingen.de/2021/03/",
        "https://tigers-tuebingen.de/2021/04/",
        "https://tigers-tuebingen.de/2021/05/",
        "https://tigers-tuebingen.de/2021/06/",
        "https://tigers-tuebingen.de/2021/07/",
        "https://tigers-tuebingen.de/2021/08/",
        "https://tigers-tuebingen.de/2021/09/",
        "https://tigers-tuebingen.de/2021/10/",
        "https://tigers-tuebingen.de/2021/11/",
        "https://tigers-tuebingen.de/2021/12/",
        "https://tigers-tuebingen.de/2022/01/",
        "https://tigers-tuebingen.de/2022/02/",
        "https://tigers-tuebingen.de/2022/03/",
        "https://tigers-tuebingen.de/2022/04/",
        "https://tigers-tuebingen.de/2022/05/",
        "https://tigers-tuebingen.de/2022/06/",
        "https://tigers-tuebingen.de/2022/07/",
        "https://tigers-tuebingen.de/2022/08/",
        "https://tigers-tuebingen.de/2022/09/",
        "https://tigers-tuebingen.de/2022/10/",
        "https://tigers-tuebingen.de/2022/11/",
        "https://tigers-tuebingen.de/2022/12/",
        "https://tigers-tuebingen.de/2023/01/",
        "https://tigers-tuebingen.de/2023/02/",
        "https://tigers-tuebingen.de/2023/03/",
        "https://tigers-tuebingen.de/2023/04/",
        "https://tigers-tuebingen.de/2023/05/",
        "https://tigers-tuebingen.de/2023/06/",
        "https://tigers-tuebingen.de/2023/07/",
        "https://tigers-tuebingen.de/akkreditierungen/",
        "https://tigers-tuebingen.de/anfahrt/",
        "https://tigers-tuebingen.de/ansprechpartner_sponsoring/",
        "https://tigers-tuebingen.de/arena/",
        "https://tigers-tuebingen.de/auslosung-bbl-pokal-am-donnerstag/",
        "https://tigers-tuebingen.de/bilder-heimspiele/",
        "https://tigers-tuebingen.de/business/hospitality/",
        "https://tigers-tuebingen.de/damen-steigen-in-die-regionalliga-auf/",
        "https://tigers-tuebingen.de/datenschutzerklaerung/",
        "https://tigers-tuebingen.de/dauerkarte/",
        "https://tigers-tuebingen.de/die-wichtigsten-regeln/",
        "https://tigers-tuebingen.de/downloads-presse/",
        "https://tigers-tuebingen.de/downloads/",
        "https://tigers-tuebingen.de/dritter-spieltag-der-aok-grundschulliga/",
        "https://tigers-tuebingen.de/easycredit-bbl-gibt-vorlaeufigen-spielplan-fuer-die-saison-2023-2024-bekannt-pokalmodus-mit-zweitligisten-startet-lizenzierung-abgeschlossen/",
        "https://tigers-tuebingen.de/fans/fanclubs/",
        "https://tigers-tuebingen.de/faq/",
        "https://tigers-tuebingen.de/gleich-mehrere-mannschaften-der-young-tigers-tuebingen-unter-den-topteams-im-laendle/",
        "https://tigers-tuebingen.de/grundschule-an-der-steinlach-gewinnt-aok-grundschulliga/",
        "https://tigers-tuebingen.de/historie/",
        "https://tigers-tuebingen.de/im-bbl-pokal-gegen-die-basketball-loewen-braunschweig/",
        "https://tigers-tuebingen.de/impressum/",
        "https://tigers-tuebingen.de/jbbl-team-gewinnt-erstes-spiel-in-crailsheim/",
        "https://tigers-tuebingen.de/jekabs-beck-wechselt-zu-den-dragons-rhoendorf/",
        "https://tigers-tuebingen.de/jobs/",
        "https://tigers-tuebingen.de/jungle-time/",
        "https://tigers-tuebingen.de/klassenerhalt-oder-drittes-spiel-in-crailsheim/",
        "https://tigers-tuebingen.de/klaus-koermoes-absolviert-erfolgreich-die-minitrainer-offensive/",
        "https://tigers-tuebingen.de/kontakt/",
        "https://tigers-tuebingen.de/laufen-fuer-den-guten-zweck-rund-700-teilnehmende-beim-14-spendenlauf-der-stadtwerke-tuebingen-tuebingen-hilft-ukraine-erhaelt-spendensumme-ueber-8-000-euro/",
        "https://tigers-tuebingen.de/linksammlung/",
        "https://tigers-tuebingen.de/management/",
        "https://tigers-tuebingen.de/mannschaft/",
        "https://tigers-tuebingen.de/medizinische-betreuung/",
        "https://tigers-tuebingen.de/mission-erfuellt-hauptamtlicher-jugendtrainer-manu-pasios-verlaesst-die-tigers-tuebingen/",
        "https://tigers-tuebingen.de/nbbl-qualifikation-runde-eins-in-tuebingen/",
        "https://tigers-tuebingen.de/nbbl-qualifikation-verpasst/",
        "https://tigers-tuebingen.de/newsletter/",
        "https://tigers-tuebingen.de/partner-werden/",
        "https://tigers-tuebingen.de/partner/",
        "https://tigers-tuebingen.de/partners/stadtwerke-tuebingen/",
        "https://tigers-tuebingen.de/player/aatu-kivimaeki/",
        "https://tigers-tuebingen.de/player/bakary-dibba/",
        "https://tigers-tuebingen.de/player/daniel-jansson-hc/",
        "https://tigers-tuebingen.de/player/daniel-keppeler/",
        "https://tigers-tuebingen.de/player/erol-ersek/",
        "https://tigers-tuebingen.de/player/gerrit-lehe/",
        "https://tigers-tuebingen.de/player/gianni-otto/",
        "https://tigers-tuebingen.de/player/hanot-zabaleta-carro-co-trainer/",
        "https://tigers-tuebingen.de/player/jhivvan-jackson/#1689858569477-c05f5497-e8cf/",
        "https://tigers-tuebingen.de/player/jimmy-boeheim/",
        "https://tigers-tuebingen.de/player/kriss-helmanis/",
        "https://tigers-tuebingen.de/player/mateo-seric/",
        "https://tigers-tuebingen.de/player/till-joenke/",
        "https://tigers-tuebingen.de/player/timo-lanmueller/#1610353348323-8e67bdae-727c/",
        "https://tigers-tuebingen.de/player/tom-walther-co-trainer/",
        "https://tigers-tuebingen.de/player/zac-darko-kelly/",
        "https://tigers-tuebingen.de/presse-kontakt/",
        "https://tigers-tuebingen.de/reichlich-bewegung-bei-den-tryouts/",
        "https://tigers-tuebingen.de/saison/news/",
        "https://tigers-tuebingen.de/saison/spielplan/",
        "https://tigers-tuebingen.de/sohn-einer-legende-kommt-nach-tuebingen-jimmy-boeheim-naechster-neuzugang/",
        "https://tigers-tuebingen.de/swt-ostercamp-2023-drei-tage-basketball-satt/",
        "https://tigers-tuebingen.de/the-puerto-rican-iverson-tigers-verpflichten-point-guard-jhivvan-jackson/",
        "https://tigers-tuebingen.de/ticket/atgb/",
        "https://tigers-tuebingen.de/ticket/gutscheine/",
        "https://tigers-tuebingen.de/tickets/",
        "https://tigers-tuebingen.de/tigers-day-in-goenningen/",
        "https://tigers-tuebingen.de/trainerfortbildung-mit-30-personen-in-tuebingen/",
        "https://tigers-tuebingen.de/tryout-der-regionalliga-mannschaft-des-sv-03-tigers-tuebingen/",
        "https://tigers-tuebingen.de/tryouts-im-nachwuchsbereich-jetzt-anmelden/",
        "https://tigers-tuebingen.de/u18-team-wird-dritter-niederlage-gegen-spaeteren-sieger-aus-karlsruhe/",
        "https://tigers-tuebingen.de/unsere-anderen-mannschaften-im-einsatz-ein-ueberblick-20/",
        "https://tigers-tuebingen.de/vertreter-der-gesellschaft/",
        "https://tigers-tuebingen.de/werte/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/aok-grundschulcup/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/camps/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/das-schulprofil-der-gss/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/fsj/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/jugendfoerderer/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/kindergarten/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/kontakt-young-tigers/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/landesliga-damen/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/leitbild/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/maennliche-jugend/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/mini-basketball/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/projekte/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/projekte/grundschulliga/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/projekte/partnerschule/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/regionalliga/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/schul-ags/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/team-u16/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/team-u18/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/tigers-coaching-academy-tca/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/verbindung-leistungssport/",
        "https://tigers-tuebingen.de/young-tigers-tuebingen/weibliche-jugend/",
        "https://tigers-tuebingen.de/zum-tod-von-manfred-steck/",
        "https://tigers-tuebingen.de/zweiter-platz-bei-den-deutsche-hochschulmeisterschaften-im-wettbewerb-drei-gegen-drei-in-tuebingen/",
        "https://tigers-tuebingen.de/zweiter-spieltag-der-aok-grundschulliga-2/",
        "https://timms.uni-tuebingen.de/",
        "https://timmscast.uni-tuebingen.de/",
        "https://tobias-bild.uni-tuebingen.de/",
        "https://tobias-lib.uni-tuebingen.de/",
        "https://tsg-tuebingen.de/",
        "https://tsg-tuebingen.de/downloads/",
        "https://tsg-tuebingen.de/kletteranlage/",
        "https://tsg-tuebingen.de/kontakt-anmeldung/",
        "https://tsg-tuebingen.de/sportzentrum1/",
        "https://tsg-tuebingen.de/tsg-gaststaette/",
        "https://tsg-tuebingen.de/verein-tsg-abc/stellenangebote/",
        "https://tsg-tuebingen.de/verein/kontakt-tsg/",
        "https://tsgtuebingen.pw-cloud.de/",
        "https://tuebilicious.mewi-projekte.de/2021/06/17/essen-und-nachhaltigkeit-in-tuebingen/",
        "https://tuebingen-derendingen.albverein.eu/vereinsheim-2/",
        "https://tuebingen-hilft-ukraine.de/en/",
        "https://tuebingen-info.de/individualreisende/oeffentliche-altstadtfuehrungen.html#c1841/",
        "https://tuebingen-info.de/stocherkahnfahrten/oeffentliche-kahnfahrten.html"
        "https://tuebingen-kultur.reservix.de/",
        "https://tuebingen-kultur.reservix.de/p/reservix/group/433693/",
        "https://tuebingen-kultur.reservix.de/p/reservix/group/435598/",
        "https://tuebingen-moshi.de/",
        "https://tuebingen-university-press.de/",
        "https://tuebingen.abstimmungs.app/",
        "https://tuebingen.ai/",
        "https://tuebingen.ai/team/",
        "https://tuebingen.artec-berlin.de/",
        "https://tuebingen.artec-berlin.de/raumbuchungssystem/showroomsforday/",
        "https://tuebingen.contigo.de/",
        "https://tuebingen.dlrg.de/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/10-tuebinger-geisterjagd-3-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/40-wuerttembergische-meisterschaften-in-5-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/aquafitness-fuer-jedermann-10-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/ausflug-der-dlrg-jugend-ins-kino-76-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/baderegeln-die-jedes-kind-versteht-40-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/bawue-masters-der-spass-stand-klar-im-82-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/bevoelkerungsschutz-ehrenzeichen-95140-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/bezirksmeisterschaften-15-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/bezirksmeisterschaften-6-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/bezirksmeisterschaften-im-hallenbad-nord-73-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/blaulichttag-2016-71-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/cocktailstand-auf-dem-stadtfest-14-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/dlrg-skifreizeit-2017-80-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/dlrg-skifreizeit-2018-84-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/dlrgler-sorgen-fuer-badesicherheit-am-42-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/drei-tage-spiel-spass-und-aktion-im-81-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/eh-training-fuer-wachgaenger-und-mitarbeiter-66-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/eine-nacht-im-tubinger-freibad-95-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/einweihungsparty-der-dlrg-jugend-im-neuen-85-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/eiskalte-tradition-neckarabschwimmen-am-32-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/eislaufen-in-der-reutlinger-eishalle-83-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/erfolgreich-ins-neue-jahr-geschwommen-50-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/erfolgreicher-zweiter-tag-in-metzingen-48-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/erstmalig-bawue-masters-in-tuebingen-4-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/etliche-stunden-arbeit-haben-sich-gelohnt-92-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/freibaduebernachtung-2019-99-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/gemutlicher-jahresabschluss-der-dlrg-jugend-97-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/girls-day-im-dlrg-raeumle-98-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/gute-platzierungen-bei-den-90-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/halloween-schwimmen-2014-34-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/halloween-schwimmen-2016-70-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/immer-bereit-die-rettungsschwimmer-der-og-30-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/impressionen-vom-weihnachstmarkt-52-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/jahreshauptversammlung-16-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/jahreshauptversammlung-2023-103657-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/jugendlager-2015-41-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/jugendlager-in-zimmern-unter-der-burg-93-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/jugendversammlung-2017-72-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/jugendversammlung-2018-88-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/landesmeisterschaften-mit-uebernachtung-in-75-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/mannschaften-koennen-sich-in-metzingen-64-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/neckarabschwimmen-2015-36-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/neckarabschwimmen-2019-87-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/neckarabschwimmen-2023-100914-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/neckarabschwimmen-26-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/neckarabschwimmen-7-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/neckarabschwimmen-eisiger-start-ins-neue-79-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/neuer-rekord-685-kilometer-im-wasser-13-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/ortsgruppe-mit-einer-mannschaft-beim-58-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/plaetzchen-und-sterne-am-1-advent-101-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/rekordwachsaison-mit-5395-stunden-94-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/rueckblick-auf-die-hauptversammlung-2018-89-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/saisoneroeffnung-im-tuebinger-freibad-69-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/seehund-nobbi-erklaert-kinderleicht-die-39-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/sieben-rettungsschwimmer-erstmals-in-konstanz-54-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/skiausfahrt-nach-hochoetz-9-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/skifahren-dlrg-freizeit-in-hochoetz-17-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/skifreizeit-am-golm-im-montafon-38-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/spieleabend-im-dlrg-raeumle-74-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/spitzen-ergebnis-beim-halloween-schwimmen-62-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/swim-around-halloween-2010-ein-29-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/swt-spendenschwimmen-102-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/uebernachtung-der-dlrg-jugend-im-freibad-77-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtliche-stimmung-am-dlrg-stand-11-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsbacken-der-jugend-15-kg-teig-78-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsbaeckerei-in-der-uhlandstrasse-100975-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsmarkt-12-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsmarkt-2010-eine-nass-kalte-28-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsmarkt-2014-35-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsmarkt-2019-100-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsmarkt-8-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/weihnachtsmarkt-wieder-einmal-voller-erfolg-96-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/winterwunderland-31-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/zehn-neue-sanitaetshelfer-in-der-ortsgruppe-56-n/",
        "https://tuebingen.dlrg.de/die-ortsgruppe/neuigkeiten/news/zwei-mannschaften-bei-den-91-n/",
        "https://tuebingen.ecogood.org/",
        "https://tuebingen.ferienprogramm-online.de/",
        "https://tuebingen.homecompany.de/en/index/",
        "https://tuebingen.institutfrancais.de/",
        "https://tuebingen.mpg.de/datenschutz/",
        "https://tuebingen.mpg.de/en/data-privacy/",
        "https://tuebingen.mpg.de/en/imprint/",
        "https://tuebingen.mpg.de/en/jobs-career/equal-opportunities/#anchor2/",
        "https://tuebingen.mpg.de/en/jobs-career/equal-opportunities/#anchor3/",
        "https://tuebingen.mpg.de/en/jobs-career/equal-opportunities/#c2118/",
        "https://tuebingen.mpg.de/impressum/",
        "https://tuebingen.mpg.de/karriere/chancengleichheit/#anchor2/",
        "https://tuebingen.mpg.de/karriere/chancengleichheit/#anchor3/",
        "https://tuebingen.mpg.de/karriere/chancengleichheit/#c2095/",
        "https://tuebingen.online-ferienbetreuung.de/",
        "https://tuebingen.r.mikatiming.de/2022/",
        "https://tuebingen.service-bw.de/web/guest/prozessstart/-/prozessstart/m40169.p1043.universalprozess-epa/re_1665-2434-1187-2787-2661-681-2188-878-2062-1807-2287-2447-2033-1532-2044_r_72070+T%C3%BCbingen/ags_08416041/le_6003865/",
        "https://tuebingen.service-bw.de/web/guest/prozessstart/-/prozessstart/m40191.p953.SBWS-ABM-AbmeldungInsAusland/re_1665-2434-1187-2787-2661-681-2188-878-2062-1807-2287-2447-2033-1532-2044_r_T%C3%BCbingen/ags_08416041/le_344/",
        "https://tuebingen.wlv-sport.de/home/bestenliste/",
        "https://tuebingen.wlv-sport.de/home/ergebnisse/",
        "https://tuebingen.wlv-sport.de/home/kinderleichtathletik/",
        "https://tuebingen.wlv-sport.de/home/kreis/",
        "https://tuebingen.wlv-sport.de/home/kreis/bestandserhebung/",
        "https://tuebingen.wlv-sport.de/home/kreis/kreisvorstand/",
        "https://tuebingen.wlv-sport.de/home/kreis/vereine-im-kreis/",
        "https://tuebingen.wlv-sport.de/home/kreis/weitere-ansprechpartner/",
        "https://tuebingen.wlv-sport.de/home/news-archiv/",
        "https://tuebingen.wlv-sport.de/home/service/",
        "https://tuebingen.wlv-sport.de/home/service/datenschutz/",
        "https://tuebingen.wlv-sport.de/home/service/impressum/",
        "https://tuebingen.wlv-sport.de/home/service/kontakt/",
        "https://tuebingen.wlv-sport.de/home/service/suche/",
        "https://tuebingen.wlv-sport.de/home/veranstaltungen/",
        "https://tuebingen.wlv-sport.de/home/veranstaltungen/bildungsveranstaltungen/",
        "https://tuebingen.wlv-sport.de/home/veranstaltungen/laufveranstaltungen/",
        "https://tuebingen.wlv-sport.de/home/veranstaltungen/weitere-veranstaltungen/",
        "https://tuebingen.wlv-sport.de/home/veranstaltungen/wettkampfveranstaltungen/",
        "https://tuebingen.wlv-sport.de/home/wettkampforganisation/",
        "https://tuebingenresearchcampus.com/",
        "https://tuebingenresearchcampus.com/de/",
        "https://tuebingenresearchcampus.com/de/datenschutz/",
        "https://tuebingenresearchcampus.com/de/news-de-de/artikel/381-interview-mit-li-zhaoping/",
        "https://tuebingenresearchcampus.com/en/",
        "https://tuebingenresearchcampus.com/en/news/artikel/376-trc-spokesperson-bernd-engler/",
        "https://tuebingenresearchcampus.com/en/news/artikel/379-interview-with-peter-dayan/",
        "https://tuebingenresearchcampus.com/en/tuebingen/",
        "https://tvstaufia.de/artikel/sport-und-kulturevent-in-tuebingen/#respond/",
        "https://twitter.com/dai_tuebingen/",
        "https://twitter.com/uktuebingen/",
        "https://ukraine.integration-kreis-tuebingen.de/",
        "https://umweltzentrum-tuebingen.de/",
        "https://umweltzentrum-tuebingen.de/wordpress/",
        "https://uni-tuebingen.de/",
        "https://uni-tuebingen.de/alumni/aus-dem-netzwerk/newsfullview-ausdemnetzwerk/article/alumni-spotlight-streng-dich-an-mach-dich-locker/",
        "https://uni-tuebingen.de/alumni/aus-dem-netzwerk/newsfullview-ausdemnetzwerk/article/tuebingen-reloaded-insights/",
        "https://uni-tuebingen.de/datenschutzerklaerung/",
        "https://uni-tuebingen.de/de/116061/",
        "https://uni-tuebingen.de/de/118876/",
        "https://uni-tuebingen.de/de/140323/",
        "https://uni-tuebingen.de/de/15463/",
        "https://uni-tuebingen.de/de/156141/",
        "https://uni-tuebingen.de/de/15967/",
        "https://uni-tuebingen.de/de/174591/",
        "https://uni-tuebingen.de/de/174711#c1560986/",
        "https://uni-tuebingen.de/de/175398/",
        "https://uni-tuebingen.de/de/176988/",
        "https://uni-tuebingen.de/de/177618/",
        "https://uni-tuebingen.de/de/180117/",
        "https://uni-tuebingen.de/de/205155/",
        "https://uni-tuebingen.de/de/216834/",
        "https://uni-tuebingen.de/de/216837/",
        "https://uni-tuebingen.de/de/216843/",
        "https://uni-tuebingen.de/de/222684/",
        "https://uni-tuebingen.de/de/232007/",
        "https://uni-tuebingen.de/de/232205/",
        "https://uni-tuebingen.de/de/232397/",
        "https://uni-tuebingen.de/de/27533/",
        "https://uni-tuebingen.de/de/2767/",
        "https://uni-tuebingen.de/de/2795/",
        "https://uni-tuebingen.de/de/2796/",
        "https://uni-tuebingen.de/de/2824/",
        "https://uni-tuebingen.de/de/45441/",
        "https://uni-tuebingen.de/de/50956/",
        "https://uni-tuebingen.de/de/61679/",
        "https://uni-tuebingen.de/de/622/",
        "https://uni-tuebingen.de/de/672/",
        "https://uni-tuebingen.de/de/905/",
        "https://uni-tuebingen.de/einrichtungen/gleichstellung/gleichstellungsbeauftragte/familienbuero/familienleben-auf-dem-campus/still-wickelmoeglichkeiten-auf-dem-campus/#c280635/",
        "https://uni-tuebingen.de/einrichtungen/gleichstellung/gleichstellungsbeauftragte/familienbuero/kinderbetreuung/",
        "https://uni-tuebingen.de/einrichtungen/gleichstellung/gleichstellungsbeauftragte/gleichstellungsbuero/",
        "https://uni-tuebingen.de/einrichtungen/gleichstellung/gleichstellungsbeauftragte/gleichstellungsbuero/athene-programm/",
        "https://uni-tuebingen.de/einrichtungen/gleichstellung/gleichstellungsbeauftragte/gleichstellungsbuero/gleichstellungsmassnahmen/",
        "https://uni-tuebingen.de/einrichtungen/personalvertretungen-beratung-beauftragte/lageplaene/karte-a-morgenstelle/auf-der-morgenstelle-16/",
        "https://uni-tuebingen.de/einrichtungen/personalvertretungen-beratung-beauftragte/lageplaene/karte-d-altstadt/alte-aula.html"
        "https://uni-tuebingen.de/einrichtungen/universitaetsbibliothek/",
        "https://uni-tuebingen.de/einrichtungen/universitaetsbibliothek/suchen-ausleihen/",
        "https://uni-tuebingen.de/einrichtungen/universitaetsbibliothek/uniarchiv/",
        "https://uni-tuebingen.de/einrichtungen/verwaltung/stabsstellen/hochschulkommunikation/testseiten-neu/alles-banane/sprachtest/barrierefreiheit/",
        "https://uni-tuebingen.de/einrichtungen/verwaltung/v-international-office/",
        "https://uni-tuebingen.de/einrichtungen/verwaltung/v-international-office/austauschprogramme/",
        "https://uni-tuebingen.de/einrichtungen/verwaltung/viii-bau-arbeitssicherheit-und-umwelt/abteilung-3/umweltmanagement-nach-emas/",
        "https://uni-tuebingen.de/einrichtungen/zentrale-einrichtungen/internationales-zentrum-fuer-ethik-in-den-wissenschaften/das-izew/",
        "https://uni-tuebingen.de/einrichtungen/zentrum-fuer-datenverarbeitung/dienstleistungen/mediendienste/videokonferenzen/",
        "https://uni-tuebingen.de/einrichtungen/zentrum-fuer-datenverarbeitung/dienstleistungen/sonstiges/it-unterstuetzung-in-corona-zeiten/",
        "https://uni-tuebingen.de/en/",
        "https://uni-tuebingen.de/en/10/",
        "https://uni-tuebingen.de/en/134527/",
        "https://uni-tuebingen.de/en/174591/",
        "https://uni-tuebingen.de/en/177618/",
        "https://uni-tuebingen.de/en/180117/",
        "https://uni-tuebingen.de/en/182071/",
        "https://uni-tuebingen.de/en/217599/",
        "https://uni-tuebingen.de/en/238572/",
        "https://uni-tuebingen.de/en/622/",
        "https://uni-tuebingen.de/en/82353/",
        "https://uni-tuebingen.de/en/84537/",
        "https://uni-tuebingen.de/en/8682/",
        "https://uni-tuebingen.de/en/alumni/from-the-network/newsfullview-fromthecommunity/article/searching-for-traces-tuebingen-10-years-later/",
        "https://uni-tuebingen.de/en/alumni/from-the-network/newsfullview-fromthecommunity/article/tuebingen-reloaded-insights/",
        "https://uni-tuebingen.de/en/data-privacy-statement/",
        "https://uni-tuebingen.de/en/einrichtungen/verwaltung/iii-studium-und-lehre/ueberfachliche-bildung-und-berufliche-orientierung/",
        "https://uni-tuebingen.de/en/einrichtungen/verwaltung/iii-studium-und-lehre/ueberfachliche-bildung-und-berufliche-orientierung/career-service/",
        "https://uni-tuebingen.de/en/einrichtungen/verwaltung/viii-bau-arbeitssicherheit-und-umwelt/abteilung-3/easy-ways-to-save-energy/",
        "https://uni-tuebingen.de/en/excellence-strategy/",
        "https://uni-tuebingen.de/en/excellence-strategy/equality/athene-programme/",
        "https://uni-tuebingen.de/en/excellence-strategy/equality/science-career-talks/",
        "https://uni-tuebingen.de/en/excellence-strategy/information/",
        "https://uni-tuebingen.de/en/excellence-strategy/information/calls-for-proposals/athene-grant/",
        "https://uni-tuebingen.de/en/excellence-strategy/information/downloads/",
        "https://uni-tuebingen.de/en/excellence-strategy/information/excellence-strategy/",
        "https://uni-tuebingen.de/en/excellence-strategy/information/faq-for-grantees/",
        "https://uni-tuebingen.de/en/excellence-strategy/research/platforms/medical-technology/",
        "https://uni-tuebingen.de/en/facilities/administration/v-international-office/",
        "https://uni-tuebingen.de/en/facilities/administration/v-international-office/exchange-programmes/",
        "https://uni-tuebingen.de/en/facilities/central-institutions/college-of-fellows/events/",
        "https://uni-tuebingen.de/en/facilities/central-institutions/international-center-for-ethics-in-the-sciences-and-humanities/team/dr-thilo-hagendorff/",
        "https://uni-tuebingen.de/en/facilities/gleichstellung/gender-equality-representative/family-office/child-care/",
        "https://uni-tuebingen.de/en/facilities/gleichstellung/gender-equality-representative/gender-equality-office/",
        "https://uni-tuebingen.de/en/facilities/gleichstellung/gender-equality-representative/gender-equality-office/athene-programm/",
        "https://uni-tuebingen.de/en/facilities/gleichstellung/gender-equality-representative/gender-equality-office/gleichstellungsmassnahmen/",
        "https://uni-tuebingen.de/en/facilities/zentrum-fuer-datenverarbeitung/services/media-services/video-conferences/",
        "https://uni-tuebingen.de/en/faculties/",
        "https://uni-tuebingen.de/en/faculties/faculty-of-economics-and-social-sciences/subjects/",
        "https://uni-tuebingen.de/en/faculties/faculty-of-humanities/research/centers-and-interdisciplinary-facilities/rhet-ai-center/",
        "https://uni-tuebingen.de/en/faculties/faculty-of-science/departments/computer-science/department/",
        "https://uni-tuebingen.de/en/faculties/faculty-of-science/departments/computer-science/department/page-4/",
        "https://uni-tuebingen.de/en/faculties/faculty-of-science/departments/computer-science/lehrstuehle/methods-of-machine-learning/personen/philipp-hennig/",
        "https://uni-tuebingen.de/en/faculties/faculty-of-science/departments/computer-science/news/newsfullview-actual/article/new-professorship-at-the-department-of-computer-science-3/",
        "https://uni-tuebingen.de/en/faculties/faculty-of-science/departments/psychology/research-groups/evolutionary-cognition-cognitive-sciences/research-group/",
        "https://uni-tuebingen.de/en/fakultaeten/juristische-fakultaet/lehrstuehle-und-personen/lehrstuehle/lehrstuehle-oeffentliches-recht/finck/",
        "https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/autonomous-vision/home/",
        "https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/maschinelles-lernen/team/prof-dr-matthias-hein/",
        "https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/methoden-des-maschinellen-lernens/personen/philipp-hennig/",
        "https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/methods-of-machine-learning/start/",
        "https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/self-organization-and-optimality-in-neuronal-networks/people/roxana-zeraati/",
        "https://uni-tuebingen.de/en/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/studium/studiengaenge/machine-learning/",
        "https://uni-tuebingen.de/en/fakultaeten/philosophische-fakultaet/fachbereiche/geschichtswissenschaft/seminareinstitute/osteuropaeische-geschichte/startseite/we-standwithukraine/",
        "https://uni-tuebingen.de/en/international/forschung/unterstuetzung-von-kooperationen/",
        "https://uni-tuebingen.de/en/international/learning-languages/",
        "https://uni-tuebingen.de/en/international/research/",
        "https://uni-tuebingen.de/en/international/study-in-tuebingen/",
        "https://uni-tuebingen.de/en/international/study-in-tuebingen/application-for-non-german-students/costs-and-funding/",
        "https://uni-tuebingen.de/en/international/study-in-tuebingen/application-for-non-german-students/faq/",
        "https://uni-tuebingen.de/en/international/study-in-tuebingen/international-phd-candidates/",
        "https://uni-tuebingen.de/en/international/studying-abroad/",
        "https://uni-tuebingen.de/en/international/teaching-training-abroad-erasmus/",
        "https://uni-tuebingen.de/en/international/welcome-center/services-for-host-institutes-1/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-cmfi/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-cmfi/cmfi/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-ifit/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-machine-learning/events/events/#c929659/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-machine-learning/home/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-machine-learning/news/news/news/newsfullview-news/article/from-canberra-to-tuebingen-robert-c-williamson-accepts-professorship-for-foundations-of-machine-learning-systems/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-machine-learning/research/research/cluster-research-groups/ethics-philosophy-lab/team/thilo-hagendorff/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-machine-learning/research/research/cluster-research-groups/professorships/explainable-machine-learning/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-machine-learning/research/research/cluster-research-groups/professorships/machine-learning-in-science/",
        "https://uni-tuebingen.de/en/research/core-research/cluster-of-excellence-machine-learning/research/research/core-facilities/machine-learning-science-colaboratory/team/",
        "https://uni-tuebingen.de/en/research/core-research/collaborative-research-centers/crc-1233/",
        "https://uni-tuebingen.de/en/research/core-research/lead-graduate-school-research-network/",
        "https://uni-tuebingen.de/en/research/support/research-funding/intramural-funding/funding-programs-in-international-research-cooperations/",
        "https://uni-tuebingen.de/en/study/finding-a-course/degree-programs-available/",
        "https://uni-tuebingen.de/en/study/profile/",
        "https://uni-tuebingen.de/en/study/profile/tuebingen-as-a-place-to-study/",
        "https://uni-tuebingen.de/en/study/student-life/student-housing/",
        "https://uni-tuebingen.de/en/universitaet/campusleben/veranstaltungen/zentrale-veranstaltungen/science-innovation-days/",
        "https://uni-tuebingen.de/en/university/",
        "https://uni-tuebingen.de/en/university/job-advertisements/job-vacancies/",
        "https://uni-tuebingen.de/en/university/news-and-publications/attempto-online/studies/newsfullview-attempto-studium-en/article/a-200-euro-one-off-payment-for-students/",
        "https://uni-tuebingen.de/en/university/news-and-publications/press-releases/press-releases/article/solidarity-with-ukraine/",
        "https://uni-tuebingen.de/en/university/organisation-and-management/university-management/vice-president-of-research/",
        "https://uni-tuebingen.de/exzellenzstrategie/",
        "https://uni-tuebingen.de/fakultaeten/evangelisch-theologische-fakultaet/fakultaet/",
        "https://uni-tuebingen.de/fakultaeten/evangelisch-theologische-fakultaet/lehrstuehle-und-institute/kirchengeschichte/kirchengeschichte-ii/mitarbeiter/vhdrecoll/",
        "https://uni-tuebingen.de/fakultaeten/evangelisch-theologische-fakultaet/studium/semester-und-studienplanung/studien-und-pruefungsordnungen/#c884293/",
        "https://uni-tuebingen.de/fakultaeten/evangelisch-theologische-fakultaet/studium/semester-und-studienplanung/studien-und-pruefungsordnungen/#c884401/",
        "https://uni-tuebingen.de/fakultaeten/juristische-fakultaet/studium/im-studium/zertifikatsstudiengaenge/recht-ethik-wirtschaft/",
        "https://uni-tuebingen.de/fakultaeten/juristische-fakultaet/studium/im-studium/zertifikatsstudiengaenge/recht-und-rhetorik/",
        "https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/geowissenschaften/arbeitsgruppen/mineralogie-geodynamik/forschungsbereich/cca-bw/cca-bw/",
        "https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/computergrafik/lehrstuhl/mitarbeiter/prof-dr-ing-hendrik-lensch/",
        "https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/computergrafik/lehrstuhl/mitarbeiter/zohreh-ghaderi/",
        "https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/data-science-analytics/team/prof-dr-gjergji-kasneci/",
        "https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/decision-making/team/jun-prof-dr-ing-setareh-maghsudi/",
        "https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/maschinelles-lernen/team/prof-dr-matthias-hein/",
        "https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/studium/studiengaenge/machine-learning/",
        "https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/altertums-und-kunstwissenschaften/mwi/institut/aktuelles/",
        "https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/aoi/koreanistik/studium/studiengaenge/makes-dual-degree-master/",
        "https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/geschichtswissenschaft/seminareinstitute/zeitgeschichte/institut/",
        "https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/englisches-seminar/sections/american-studies/",
        "https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/forschung/graduiertenakademie/digitales-grossprojekt-promotion-2020/kursbeschreibungen/",
        "https://uni-tuebingen.de/fakultaeten/wirtschafts-und-sozialwissenschaftliche-fakultaet/faecher/fachbereich-sozialwissenschaften/ifp/institut/",
        "https://uni-tuebingen.de/fakultaeten/wirtschafts-und-sozialwissenschaftliche-fakultaet/faecher/fachbereich-sozialwissenschaften/soziologie/",
        "https://uni-tuebingen.de/fakultaeten/wirtschafts-und-sozialwissenschaftliche-fakultaet/faecher/fachbereich-sozialwissenschaften/sportwissenschaft/institut/",
        "https://uni-tuebingen.de/fakultaeten/wirtschafts-und-sozialwissenschaftliche-fakultaet/faecher/fachbereich-sozialwissenschaften/sportwissenschaft/studium/studienbewerber/sporteingangspruefung/",
        "https://uni-tuebingen.de/forschung/forschungsschwerpunkte/exzellenzcluster-cmfi/aktuelles/news/newsfullview-aktuelles/article/neuer-ansatz-gegen-nebenwirkungen-von-antibiotika-1/",
        "https://uni-tuebingen.de/forschung/forschungsschwerpunkte/exzellenzcluster-cmfi/aktuelles/news/newsfullview-aktuelles/article/neuer-ansatz-gegen-nebenwirkungen-von-antibiotika-1/ /",
        "https://uni-tuebingen.de/forschung/forschungsschwerpunkte/exzellenzcluster-maschinelles-lernen/forschung/forschung/cluster-arbeitsgruppen/professuren/foundations-of-machine-learning-systems/",
        "https://uni-tuebingen.de/forschung/forschungsschwerpunkte/exzellenzcluster-maschinelles-lernen/home/",
        "https://uni-tuebingen.de/forschung/forschungsschwerpunkte/graduiertenkollegs/gk-religioeses-wissen/praxisprojekte/app-projekt-tuebinger-geschichten/",
        "https://uni-tuebingen.de/forschung/innovation/startup-center/kontakt/",
        "https://uni-tuebingen.de/forschung/innovation/startup-center/veranstaltungen/startupcon-tuebingen/",
        "https://uni-tuebingen.de/forschung/innovation/technologietransfer/gruenderinnen-und-gruender/",
        "https://uni-tuebingen.de/forschung/nachwuchsfoerderung/graduiertenakademie/",
        "https://uni-tuebingen.de/forschung/service/forschungsfoerderung/",
        "https://uni-tuebingen.de/international/studierende-aus-dem-ausland/bewerbung-fuer-internationale-studierende/faq/",
        "https://uni-tuebingen.de/international/studierende-aus-dem-ausland/sommerkurse-und-kurzzeit-programme/international-european-studies/",
        "https://uni-tuebingen.de/international/welcome-center/service-fuer-gastgebende-institutionen-1/",
        "https://uni-tuebingen.de/lehrende/digitale-lehre/screencast/",
        "https://uni-tuebingen.de/lehrende/digitale-lehre/seminar/#c1057050/",
        "https://uni-tuebingen.de/lehrende/digitale-lehre/seminar/#c1057053/",
        "https://uni-tuebingen.de/lehrende/digitale-lehre/seminar/#c1057065/",
        "https://uni-tuebingen.de/lehrende/digitale-lehre/vorlesung/#c1058472/",
        "https://uni-tuebingen.de/lehrende/digitale-lehre/vorlesung/#c1283517/",
        "https://uni-tuebingen.de/lehrende/digitale-lehre/zoerr/",
        "https://uni-tuebingen.de/lehrende/hochschuldidaktik/",
        "https://uni-tuebingen.de/lehrende/hochschuldidaktik/workshops/zertifikatsprogramm/workshops/freie-plaetze-im-sommer-2023/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/downloads/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/gremien/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/preise-und-ausschreibungen/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/prozesse/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/themen/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/veranstaltungen/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/verstaendnis/",
        "https://uni-tuebingen.de/lehrende/studiengangsplanung-und-entwicklung/widerspruchsverfahren/",
        "https://uni-tuebingen.de/si-days/",
        "https://uni-tuebingen.de/studium/beratung-und-info/studieren-mit-beeintraechtigung/",
        "https://uni-tuebingen.de/studium/berufsorientierung/unternehmenskontakte/career-day/",
        "https://uni-tuebingen.de/studium/rund-ums-studium/studentisches-engagement/gruppen-und-initiativen/",
        "https://uni-tuebingen.de/studium/studienangebot/schluesselqualifikationen-das-studium-professionale/kursinformationen/",
        "https://uni-tuebingen.de/studium/studienangebot/schluesselqualifikationen-das-studium-professionale/zertifikate/",
        "https://uni-tuebingen.de/studium/studienangebot/ueberfachliche-kompetenzen/gesellschaftliches-engagement/studentisches-engagement/engagementransfer/#c1540342/",
        "https://uni-tuebingen.de/studium/studienangebot/verzeichnis-der-studiengaenge/",
        "https://uni-tuebingen.de/studium/studienangebot/verzeichnis-der-studiengaenge/detail/course/naturwissenschaft-und-technik-lehramt-gymnasium-bachelor-of-education-hauptfach/",
        "https://uni-tuebingen.de/studium/studieninteresse/angebote-fuer-schulen/",
        "https://uni-tuebingen.de/studium/studieninteresse/angebote-fuer-studieninteressierte/",
        "https://uni-tuebingen.de/tuefff/",
        "https://uni-tuebingen.de/universitaet/aktuelles-und-publikationen/attempto-online/studium/newsfullview-attempto-studium/article/200-euro-einmalzahlung-fuer-studierende/",
        "https://uni-tuebingen.de/universitaet/aktuelles-und-publikationen/newsletter-uni-tuebingen-aktuell/2023/1/leute/8/",
        "https://uni-tuebingen.de/universitaet/aktuelles-und-publikationen/newsletter-uni-tuebingen-aktuell/2023/2/leute/4/",
        "https://uni-tuebingen.de/universitaet/aktuelles-und-publikationen/pressekontakt/",
        "https://uni-tuebingen.de/universitaet/aktuelles-und-publikationen/pressemitteilungen/newsfullview-pressemitteilungen/article/erhebliche-auswirkungen-der-geplanten-regionalstadtbahn-auf-die-universitaet/",
        "https://uni-tuebingen.de/universitaet/aktuelles-und-publikationen/veroeffentlichungen/",
        "https://uni-tuebingen.de/universitaet/campusleben/kunst-kultur-und-freizeit/collegium-musicum/",
        "https://uni-tuebingen.de/universitaet/campusleben/kunst-kultur-und-freizeit/collegium-musicum/akademischer-chor/",
        "https://uni-tuebingen.de/universitaet/campusleben/kunst-kultur-und-freizeit/collegium-musicum/akademisches-orchester/",
        "https://uni-tuebingen.de/universitaet/campusleben/veranstaltungen/veranstaltungskalender/kongresse-und-tagungen/social-justice-and-technological-futures/",
        "https://uni-tuebingen.de/universitaet/campusleben/veranstaltungen/zentrale-veranstaltungen/kinder-uni/",
        "https://uni-tuebingen.de/universitaet/campusleben/veranstaltungen/zentrale-veranstaltungen/science-innovation-days/",
        "https://uni-tuebingen.de/universitaet/campusleben/veranstaltungen/zentrale-veranstaltungen/science-innovation-days/si-days-020722/#c1583873/",
        "https://uni-tuebingen.de/universitaet/campusleben/veranstaltungen/zentrale-veranstaltungen/sommeruniversitaet/",
        "https://uni-tuebingen.de/universitaet/campusleben/veranstaltungen/zentrale-veranstaltungen/studium-generale/",
        "https://uni-tuebingen.de/universitaet/campusleben/veranstaltungen/zentrale-veranstaltungen/tuefff-tuebinger-fenster-fuer-forschung/",
        "https://uni-tuebingen.de/universitaet/profil/freunde-und-foerderer/universitaetsbund/",
        "https://uni-tuebingen.de/universitaet/profil/geschichte-der-universitaet/aufarbeitung-ns-zeit/",
        "https://uni-tuebingen.de/weiterbildung/",
        "https://uni-tuebingen.de/weiterbildung/programm/geodatenmanager-in/",
        "https://uni-tuebingen.de/zh/fakultaeten/philosophische-fakultaet/fachbereiche/altertums-und-kunstwissenschaften/ur-und-fruehgeschichte-und-archaeologie-des-mittelalters/abteilungen/mittelalter/forschungsprojekte/abgeschlossene-projekte/stiftskirche-digital/",
        "https://uni-tuebingen.de/zielgruppen/weiterbildung/programm/integrative-sozialarbeit/",
        "https://uni-tuebingen.de/zielgruppen/weiterbildung/programm/versicherungsmedizin/",
        "https://unser-tuebingen.de/",
        "https://unser-tuebingen.de/1821-neueroeffnung-restaurant-mit-ambiente-in-der-innenstadt-von-tuebingen/",
        "https://unser-tuebingen.de/author/wendyadmin/",
        "https://unser-tuebingen.de/category/ausflugstipps/",
        "https://unser-tuebingen.de/category/entertainment/",
        "https://unser-tuebingen.de/category/essentrinken/",
        "https://unser-tuebingen.de/category/lifestyle/",
        "https://unser-tuebingen.de/category/rezept/",
        "https://unser-tuebingen.de/category/stadtnews/",
        "https://unser-tuebingen.de/category/stadtnews/events/",
        "https://unser-tuebingen.de/category/stadtnews/uebernachten/",
        "https://unser-tuebingen.de/category/stadtnews/wohnen/",
        "https://unser-tuebingen.de/category/wohnen/",
        "https://unser-tuebingen.de/datenschutzerklaerung/",
        "https://unser-tuebingen.de/faros-tuebingen-griechischisch-essen/",
        "https://unser-tuebingen.de/hello-world/",
        "https://unser-tuebingen.de/impressum/",
        "https://unser-tuebingen.de/my-bookmarks/",
        "https://unser-tuebingen.de/schwaebische-tapas-im-gasthaus-baeren/",
        "https://unser-tuebingen.de/teilnahmebedingungen-gewinnspiele-und-verlosungen/",
        "https://unser-tuebingen.de/veranstalter/schummeltag-tuebingen-street-food-festival/",
        "https://unser-tuebingen.de/veranstaltung-in-tuebingen-bearbeiten/",
        "https://unser-tuebingen.de/veranstaltung-in-tuebingen-einreichen/",
        "https://unser-tuebingen.de/veranstaltung/apero-litteraire-in-bebenhausen/",
        "https://unser-tuebingen.de/veranstaltung/clubbing-frau-holle/2023-09-22/",
        "https://unser-tuebingen.de/veranstaltung/mexican-weekend-2/",
        "https://unser-tuebingen.de/veranstaltung/platzkonzerte-auf-dem-marktplatz-2/",
        "https://unser-tuebingen.de/veranstaltung/sommerfest-pop-up-gemeinschaftsgarten-eisenbahnstr/",
        "https://unser-tuebingen.de/veranstaltungen-tuebingen-kalender/",
        "https://unser-tuebingen.de/veranstaltungskalender/",
        "https://unser-tuebingen.de/veranstaltungskalender/kategorie/essen-trinken/",
        "https://unser-tuebingen.de/veranstaltungskalender/kategorie/festival/",
        "https://unser-tuebingen.de/veranstaltungsort/festplatz-tuebingen/",
        "https://unser-tuebingen.de/vietnamesisch-essen-tuebingen-das-an-an/",
        "https://unser-tuebingen.de/weinbergfest-wurmlingen-romantisches-weinfest-vor-den-toren-tuebingens/",
        "https://uro-tuebingen.de/about-us-ru/clinical-care.html"
        "https://uro-tuebingen.de/about-us-ru/clinical-consultation-hour.html"
        "https://uro-tuebingen.de/about-us-ru/outpatient-treatment.html"
        "https://uro-tuebingen.de/about-us-ru/team.html"
        "https://uro-tuebingen.de/about-us/clinical-care.html"
        "https://uro-tuebingen.de/about-us/clinical-consultation-hour.html"
        "https://uro-tuebingen.de/about-us/clinical-studies.html"
        "https://uro-tuebingen.de/about-us/donation-for-research-and-teaching.html"
        "https://uro-tuebingen.de/about-us/outpatient-treatment.html"
        "https://uro-tuebingen.de/about-us/teaching-and-advanced-training.html"
        "https://uro-tuebingen.de/about-us/team.html"
        "https://uro-tuebingen.de/contact-ru/contact.html"
        "https://uro-tuebingen.de/contact/contact.html"
        "https://uro-tuebingen.de/contact/legal-notice.html"
        "https://uro-tuebingen.de/die-klinik/forschung/graduiertenkolleg-2543.html"
        "https://uro-tuebingen.de/home-en.html"
        "https://uro-tuebingen.de/home-ru.html"
        "https://uro-tuebingen.de/services-ru.html"
        "https://uro-tuebingen.de/services-ru/reconstructive-urology-and-neurourology.html"
        "https://uro-tuebingen.de/services.html"
        "https://uro-tuebingen.de/services/reconstructive-urology-and-neurourology.html"
        "https://vergil.uni-tuebingen.de/seatfinder/seatfinder.html"
        "https://vincentberenz.is.tuebingen.mpg.de/",
        "https://vitruv.uni-tuebingen.de/ilias3/goto_pr01_cat_6516.html"
        "https://vitruv.uni-tuebingen.de/ilias3/goto_pr01_cat_6573.html"
        "https://vitruv.uni-tuebingen.de/ilias3/goto_pr01_cat_6579.html"
        "https://vpngw2.tuebingen.mpg.de/",
        "https://wayback.archive-it.org/9027/20110817223223/",
        "https://www.tuebingen.de/pressemitteilungen/25_23745.html"
        "https://web.archive.org/web/19970801000000*/www.tuebingen.de/",
        "https://webdav.tuebingen.mpg.de/causality/",
        "https://webmail.uni-tuebingen.de/",
        "https://weltladen-tuebingen.de/joomla/bildungsarbeit/stadtrundgaenge.html"
        "https://www-ub.ub.uni-tuebingen.de/dienste/cgi-bin/avorschlag.cgi/",
        "https://www.aaw-tuebingen.de/joomla/bildungsarbeit.html#Bildungsmaterial/",
        "https://www.abfall-kreis-tuebingen.de/",
        "https://www.abfall-kreis-tuebingen.de/abfall-abc/",
        "https://www.abfall-kreis-tuebingen.de/abfallberatung/",
        "https://www.abfall-kreis-tuebingen.de/abfuhrkalender-2023/",
        "https://www.abfall-kreis-tuebingen.de/aktuelles/altpapier-2018/",
        "https://www.abfall-kreis-tuebingen.de/datenschutz/",
        "https://www.abfall-kreis-tuebingen.de/die-website-im-ueberblick/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen-wohin-mit-den-abfaellen-problemstoffsammelstellen/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen-wohin-mit-den-abfaellen-problemstoffsammelstellen/geaenderte-oeffnungszeiten-und-schliessungen/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallbehaelter-abfallsaecke/abfallsaecke/gelbe-saecke/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallbehaelter-abfallsaecke/abfallsaecke/inlettsaecke/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallbehaelter-abfallsaecke/abfallsaecke/laubsaecke/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallbehaelter-abfallsaecke/abfallsaecke/restmuellsaecke/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallbehaelter-abfallsaecke/behaelterarten/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallvermeidung/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallvermeidung/8777-2/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/abfallvermeidung/windelprojekt/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/datentraeger-recycling/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/foodsharing/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/gebrauchtwaren/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/hausratverwertung/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/kostenlose-kleinanzeigen/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/reparatur-cafe/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/second-hand-laeden/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/soziale-kleiderlaeden/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/umsonstlaeden/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/warentauschtage/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/welche-abfaelle-habe-ich/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/bauschutt-erddeponien/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/container-standorte/altglascontainer-stadt-tuebingen/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/container-standorte/altkleidercontainer_stadt_tue/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/container-standorte/altpapiercontainer/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/entsorgungszentrum-dusslingen-2/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/entsorgungszentrum-dusslingen/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/haeckselplaetze/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/private-verwerter/",
        "https://www.abfall-kreis-tuebingen.de/entsorgen/wohin-mit-den-abfaellen/weihnachtsbaumabholung-2/",
        "https://www.abfall-kreis-tuebingen.de/express-sonderabfuhren/",
        "https://www.abfall-kreis-tuebingen.de/faq-biotonne-landkreis-tuebingen/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren-ermitteln/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/anmeldeformular-pdf/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/gebuehrenarchiv/gebuehrenarchiv-gewerbe/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/gebuehrenarchiv/gebuehrenarchiv-privathaushalte/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/kontakt-gebuehrenabteilung/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/privat-oder-gewerbe/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/privathaushalt/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/privathaushalt/anmeldung-privathaushalte-neu/",
        "https://www.abfall-kreis-tuebingen.de/gebuehren/privathaushalt/gebuhrenubersicht/",
        "https://www.abfall-kreis-tuebingen.de/gebuehrenrechner/",
        "https://www.abfall-kreis-tuebingen.de/gelber-sack-faqs/",
        "https://www.abfall-kreis-tuebingen.de/geraeteverleih/",
        "https://www.abfall-kreis-tuebingen.de/gewerbebetrieb/",
        "https://www.abfall-kreis-tuebingen.de/gewerbebetrieb/anmeldung-gewerbe/",
        "https://www.abfall-kreis-tuebingen.de/gewerbebetrieb/gebuhrenubersicht/",
        "https://www.abfall-kreis-tuebingen.de/impressum/",
        "https://www.abfall-kreis-tuebingen.de/informatives/formulare/",
        "https://www.abfall-kreis-tuebingen.de/informatives/haeufig-gestellte-fragen/",
        "https://www.abfall-kreis-tuebingen.de/informatives/informationsbroschueren/",
        "https://www.abfall-kreis-tuebingen.de/informatives/mediathek/",
        "https://www.abfall-kreis-tuebingen.de/informatives/mediathek/film-herr-stinknich-umweltbildung/",
        "https://www.abfall-kreis-tuebingen.de/informatives/mediathek/infokisten/",
        "https://www.abfall-kreis-tuebingen.de/informatives/mediathek/muellsortierspiel/",
        "https://www.abfall-kreis-tuebingen.de/informatives/presseschau/",
        "https://www.abfall-kreis-tuebingen.de/informatives/presseschau/muellecken-pressemitteilungen/",
        "https://www.abfall-kreis-tuebingen.de/informatives/satzungen/",
        "https://www.abfall-kreis-tuebingen.de/informatives/satzungen/abfallwirtschaftssatzung/",
        "https://www.abfall-kreis-tuebingen.de/informatives/satzungen/awb-betriebssatzung/",
        "https://www.abfall-kreis-tuebingen.de/informatives/satzungen/zwecksverbandssatzung/",
        "https://www.abfall-kreis-tuebingen.de/informatives/schulen-kindergaerten/abfallberatung-in-kindergaerten/",
        "https://www.abfall-kreis-tuebingen.de/informatives/schulen-kindergaerten/abfallberatung-in-schulen/",
        "https://www.abfall-kreis-tuebingen.de/informatives/schulen-kindergaerten/abfallerlebnispfad/",
        "https://www.abfall-kreis-tuebingen.de/informatives/veranstaltungen/",
        "https://www.abfall-kreis-tuebingen.de/informatives/veranstaltungen/wissenswertes-zum-thema-verpackungsabfall/",
        "https://www.abfall-kreis-tuebingen.de/kasse/",
        "https://www.abfall-kreis-tuebingen.de/kontakt-2/",
        "https://www.abfall-kreis-tuebingen.de/kontakt/",
        "https://www.abfall-kreis-tuebingen.de/linkliste-umweltbildung/",
        "https://www.abfall-kreis-tuebingen.de/medienliste-des-kreismedienzentrums/",
        "https://www.abfall-kreis-tuebingen.de/online-abfuhrtermine/",
        "https://www.abfall-kreis-tuebingen.de/online-sonderabfuhren/",
        "https://www.abfall-kreis-tuebingen.de/page/2/",
        "https://www.abfall-kreis-tuebingen.de/reparaturfuehrer-reparieren-statt-wegwerfen/",
        "https://www.abfall-kreis-tuebingen.de/services/bestellung-altpapiertonne/",
        "https://www.abfall-kreis-tuebingen.de/services/muellwecker/",
        "https://www.abfall-kreis-tuebingen.de/services/reklamationen/",
        "https://www.abfall-kreis-tuebingen.de/services/tuebinger-abfall-app/",
        "https://www.abfall-kreis-tuebingen.de/services/zugang-zum-servicecenter/",
        "https://www.abfall-kreis-tuebingen.de/sonderabfuhren-ab-2023/",
        "https://www.abfall-kreis-tuebingen.de/sonderabfuhren-bestellen-ab-2023-faqs/",
        "https://www.abfall-kreis-tuebingen.de/vermeiden/unverpackt-laeden/",
        "https://www.abfall-kreis-tuebingen.de/wie-funktionieren-die-online-abfuhrtermine/",
        "https://www.abfall-kreis-tuebingen.de/woechentliche-leerung-der-biotonne/",
        "https://www.ablesen.de/tuebingen/",
        "https://www.adfc-bw.de/tuebingen/service/fahrradflohmarkt/",
        "https://www.adventgemeinde-tuebingen.de/",
        "https://www.africa-tuebingen.de/",
        "https://www.agit-tuebingen.de/",
        "https://www.akbw.de/wir-ueber-uns/kammerbezirke/tbingen/kammergruppen/tuebingen.html"
        "https://www.altekunst-tuebingen.de/",
        "https://www.altenberatung-tuebingen.de/",
        "https://www.altenhilfe-tuebingen.de/",
        "https://www.amazon.jobs/en/locations/tubingen-germany/",
        "https://www.ambrosianum-tuebingen.de/",
        "https://www.amsel.de/tuebingen/aktuelles/",
        "https://www.amtsgericht-tuebingen.de/",
        "https://www.antiquitaeten-tuebingen.de/",
        "https://www.antiquitaeten-tuebingen.de/anfahrt/",
        "https://www.antiquitaeten-tuebingen.de/bronze/art-nr-b1-bronzefigur-mit-der-darstellung-eines-floete-spielenden-juenglings-um-1900/",
        "https://www.antiquitaeten-tuebingen.de/bronze/art-nr-b5-bronzeskulptur-bergmann-um-1900-20/",
        "https://www.antiquitaeten-tuebingen.de/datenschutz/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/aquarellzeichnung-hoelderlinturm-tuebingen-art-nr-g1194/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/aquarellzeichnung-schloss-strehla-bei-meissen-w-bruecher-1856-art-nr-g1313/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/art-nr-g1293-getoente-lithografie-mit-einem-blick-auf-stuttgart-von-robert-f-stieler-1877/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/art-nr-g1296-lithografie-mit-einer-ansicht-auf-die-stadt-tuebingen-von-robert-stieler-um-1870/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/art-nr-g1300-getoente-lithografie-mit-einer-ansicht-auf-das-schloss-lichtenstein-von-robert-f-stieler-um-1870/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/blumenstilleben-art-nr-g1260/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/farblithografie-mit-einem-blick-auf-ravensburg-von-carl-baumann-nach-robert-stieler-ende-19-jh-art-nr-g1302/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/farblithografie-mit-einer-ansicht-aus-reutlingen-von-robert-stieler-1878-art-nr-g1298/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/getoente-lithografie-mit-einer-ansicht-auf-die-burg-hohenzollern-von-robert-f-stieler-1878-art-nr-g1299/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/getoente-lithografie-mit-einer-ansicht-der-klosteranlage-maulbronn-von-robert-f-stieler-1878-g1297/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/kleinformatiges-oelgemaelde-auf-einer-keramikfliese-mit-der-darstellung-einer-alpenlandschaft-art-nr-g1319/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/kupferstich-der-abschied-des-muellers-von-j-wagner-nach-einer-zeichnung-von-carl-reinhart-1801-art-nr-g1314/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/lithografie-mit-einer-ansicht-aus-ulm-mit-dem-muenster-von-robert-f-stieler-1878-art-nr-g1301/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/lithografie-urach-louis-rachel-um-1870-art-nr-g1295/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/oelgemaelde-biedermeier-art-nr-g1316-um-1820-30/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/oelgemaelde-kreuzabnahme-wohl-januarius-zick-ende-18-jh-g1317/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/oelgemaelde-landschaft-mondlicht-egbert-patzig-art-nr-g1320/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/oelgemaelde-muehle-20-jh-g1321-frederick-arthur-bridgman/",
        "https://www.antiquitaeten-tuebingen.de/gemaelde/oelgemaelde-segelschiff-ehlert-1950-art-nr-g1281/",
        "https://www.antiquitaeten-tuebingen.de/impressum/",
        "https://www.antiquitaeten-tuebingen.de/katalog/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/aufsatzmoebel/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/aufsatzmoebel/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/gemaelde/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/gemaelde/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/gemaelde/seite/45/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/grafik/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/grafik/seite/21/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/grafik/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/kommoden/seite/14/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/kommoden/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/kommoden/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/lampen/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/porzellan/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/porzellan/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/schmuck/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/schmuck/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/schmuck/seite/7/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/schraenke/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/schraenke/seite/28/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/schraenke/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sekretaere/seite/13/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sekretaere/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sekretaere/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/silber/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/silber/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sitzmoebel/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sitzmoebel/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sitzmoebel/seite/34/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sonstiges/seite/15/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sonstiges/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/sonstiges/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/spiegel/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/spiegel/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/spiegel/seite/7/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/tische/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/tische/seite/21/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/tische/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/uhren/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/uhren/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/uhren/seite/7/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/vitrinen/seite/12/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/vitrinen/seite/2/",
        "https://www.antiquitaeten-tuebingen.de/kategorie/vitrinen/seite/3/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/art-nr-10273-barockkommode-mit-schreibpultaufsatz-sueddeutsch-2-haelfte-18-jh/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/art-nr-3313-modellkommode-mitte-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/art-nr-5759-aufsatzkommode-mit-orig-farbl-fassung-allgaeu-1717/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/art-nr-6026-italienischer-barockkommode-2-haelfte-18-jahrhundert-nussbaumwurzel/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/art-nr-6093-grosser-barockaufsatzsekretaer-wohl-bamberg-mitte-18-jh/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/art-nr-6106-kirschbaumaufsatzsekretaer-bez-sueddeutschland-1861/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/biedermeier-kommode-mit-vollsaeulen-um-1820-art-nr-10276/",
        "https://www.antiquitaeten-tuebingen.de/kommoden/haengevitrine-vitrinenaufsatz-kirschbaum-19-jh-art-6190/",
        "https://www.antiquitaeten-tuebingen.de/kontakt/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-3048-empirewandapplike-frankreich-anfang-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-4922-deckenleuchter-mit-kristallglasbehang-messingmontierung-mitte-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-4958-deckenlampe-6-flammig-messing-getrieben-versilbert-um-1920-30/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-4971-jugendstildeckenlampe-eisen-geschmiedet-um-1900/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-5224-grosser-deckenleuchter-mit-kristallprismen-16-flm-um-1930/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-5229-paar-barocke-dekorationen-mitte-18-jh/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-5473-deckenleuchter-im-empirestil-2-haelfte-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-5548-jugendstildeckenleuchter-in-messing-4-flammig-um-1900/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-5589-deckenleuchter-holz-geschnitzt-vergoldet-um-1880/",
        "https://www.antiquitaeten-tuebingen.de/lampen/art-nr-5713-paar-feuervergoldet-wandappliken-in-bronze-um-1800/",
        "https://www.antiquitaeten-tuebingen.de/lieferung/",
        "https://www.antiquitaeten-tuebingen.de/merkliste/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p40-96-teiliges-speiseservice-mit-kupfergruener-blumenmalerei-und-goldstaffage-fuer-12-personen-porzellanmanufaktur-nymphenburg-2-haelfte-20-jh-2/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p43-kleine-teekanne-mit-purpurbemalung-porzellanmanufaktur-hoechster-um-1770-1780/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p44-servierplatte-aus-porzellan-mit-purpurbemalung-entwurf-carl-eugen-ludwigsburger-porzellanmanufaktur-um-1770/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p45-jugendstil-porzellanfigur-junges-maedchen-mit-wildgans-thueringen-karl-ens-porzellanfabrik-volkstedt-um-1920-30/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p46-kleine-porzellandose-in-form-eines-altars-mit-eingesetztem-spiegel-wohl-thueringen-um-1900/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p47-art-deco-porzellan-deckeldose-der-firma-tillowitz-aus-schlesien-um-1920/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p49-charakter-krug-in-form-eines-mannes-mit-brille-und-hut-england-royal-dulton-20-jahrhundert/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p50-kleine-korbschale-mit-durchbrochenem-rand-und-polychromer-blumenbemalung-saechsische-porzellan-manufaktur-dresden-mitte-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p51-dreieckige-anbieteschale-aus-porzellan-mit-ausgestochenem-rand-und-polychromer-bemalung-mit-goldrand-porzellanmanufaktur-hoechster-um-1770-80/",
        "https://www.antiquitaeten-tuebingen.de/porzellan/art-nr-p52-porzellanfigurengruppe-mit-der-darstellung-eines-liebespaares-mit-taeubchen-firma-volkstedt-thueringen-wohl-mitte-2-haelfte-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/restaurierung/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/anhaenger/anhaenger-citrin-silber-gold-art-nr-j149/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/armreif-gold-art-nr-j150/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/art-deco-armband-um-1910-art-nr-j151/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/brosche-in-333-gelbgold-mit-blautopas-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/brosche-rotgold-halbperlen-opal-art-nr-j157/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/jugendstil-anhaenger-gold-rubin-perle-art-nr-j148/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/ring-gold-opal-art-nr-j153/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/ring-gold-saphir-diamanten-art-nr-j152/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/ring-weissgold-opaltriplette-diamanten-art-nr-j154/",
        "https://www.antiquitaeten-tuebingen.de/schmuck/siegelring-gold-karneol-art-nr-j155/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/anrichte-frankreich-mit-verglastem-aufsatz-um-1890-art-nr-6182/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-10181-spaetbiedermeieraufsatzvitrine-in-kirschbaum-mitte-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-3522-vitrinenaufsatz-anf-jh-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-5787-barocker-eckschrank-in-nussbaum-oesterreich-ende-18-jh/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-5915-historistisches-aufsatzbuffet-im-stil-eines-ulmer-renaissance-schrankes/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-5974-biedermeiereckschrank-in-kirschbaum-um-1830/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-5975-biedermeierbuecherschrank-in-nussbaum-um-1840/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-606-vitrinenschrank-in-nussbaum-louis-philippe-um-1850/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/art-nr-6137-grosse-ausstellungsvitrine-buecherschrank-frankreich-um-1880/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/barockschrank-flammleisten-eintuerig-um-1700-art-nr-6203/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/barockschrank-nussbaum-art-nr-6193/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/biedermeier-buecherschrank-nussbaum-sueddeutsch-um-1830-art-nr-6148/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/biedermeierschrank-eintuerig-oesterreich-um-1840-art-nr-10293/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/biedermeierschrank-nussbaum-um-1820-art-nr-10294/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/eckschrank-barock-stil-2-haelfte-19-jh-art-nr-6172/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/eckschrank-biedermeier-mahagoni-norddeutsch-um-1830-art-nr-6197/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/franzoesischer-schrank-verspiegelt-um-1880-art-nr-6195/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/grosses-jugendstil-buffet-berlin-um-1900-art-nr-6149/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/mahagoni-eckschrank-norddeutsch-um-1820-art-nr-6183/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/pfeilerschraenkchen-nussbaum-reich-intarsiert-oesterreich-ungarn-mitte-19-jahrhundert-art-nr-6125/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/schmaler-biedermeier-buecherschrank-in-nussbaum-mitte-19-jh-art-10288/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/seltenes-weichholzbuffet-fuer-kinder-um-1870-art-nr-5228/",
        "https://www.antiquitaeten-tuebingen.de/schraenke/weichholzschrank-orig-bemalung-anf-19-jh-art-nr-6179/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/art-nr-10261-empireschreibschrank-in-mahagoni-frankreich-anfang-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/art-nr-10275-biedermeier-schreibschrank-nussbaum-sueddeutsch-um-1830/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/art-nr-10285-biedermeier-schreibschrank-nussbaum/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/art-nr-5886-louis-seize-aufsatzsekretaer-um-1800/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/art-nr-6110-louis-seize-zylinderbuero-rheinland-18-jh/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/artnr-6121-tabernakelsekretaer-sueddeutsch-eventuell-oesterreich-mitte-18-jh/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/biedermeier-schreibschrank-sekretaer-nussbaum-sueddeutsch-um-1830-art-nr-10285/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/biedermeier-zylinderbuero-mit-aufbau-um-1820/",
        "https://www.antiquitaeten-tuebingen.de/sekretaere/schreibschrank-ahorneinlagen-norddeutsch-um-1830-40-art-nr-6188/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s37-milchkaennchen-und-zucker-deckeldose-aus-sterling-bremer-werkstaetten-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s38-dreiteilige-teegarnitur-mit-kanne-sahne-und-zuckergefaess-in-sterlingsilber-birmingham-1912/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s42-kaffee-und-tee-garnitur-in-800-silber-hammerschlagoptik-deutschland-um-1920-30/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s43-kernstueck-kaffeetafelset-in-silber-firma-bruckmann-heilbronn-und-c-osterberg-stuttgart-um-1870-80/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s44-kleine-ovale-schale-aus-925er-silber-amerika-fa-gorham-anfang-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s45-gewuerzgefaess-in-13-loetigem-silber-mit-originalem-glaseinsatz-um-1800/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s46-korbschale-mit-durchbrochenem-rand-in-925er-silber-bez-l-argentum-20-jh/",
        "https://www.antiquitaeten-tuebingen.de/silber/art-nr-s47-gewuerzstreuer-in-silber-auf-3-fuessigem-stand-england-ende-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/silber/paar-silberleuchter-barock-art-nr-s49/",
        "https://www.antiquitaeten-tuebingen.de/silber/teedose-deckeldose-silber-jugendstil-art-nr-s50/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/5-polsterstuehle-schaufelstuehle-kirschbaum-biedermeier-stil-um-1900-art-nr-6196/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/art-nr-6108-polsterstuhl-niederlande-mitte-18-jh/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/art-nr-6109-zwei-polsterstuehle-in-kirschbaum-sueddeutsch-1830/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/art-nr-6117-armlehnsessel-in-mahagoni-frankreich-mitte-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/sofa-sitzbank-im-klassizistischen-stil-frankreich-ende-19-jh-art-nr-6021/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/stuhl-historismus-sogen-lutherstuhl-nach-vorlage-eines-gotischen-drehstuhls-ende-19-jh-art-nr-6111/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/vier-brettstuehle-muenchner-kindl-ca-1880-1890-art-nr-6076/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/vier-polsterstuehle-im-biedermeier-stil-kirschbaum-um-1900-art-nr-6146/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/windorstuhl-england-art-nr-6176-um-1820-60/",
        "https://www.antiquitaeten-tuebingen.de/sitzmoebel/windorstuhl-england-ruester-art-nr-6175/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/art-deco-teewagen-deutschland-um-1920-art-nr-6184/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/doppel-bilderrahmen-versilbert-jugendstil-art-nr-s48/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/grosse-kaminumrahmung-eiche-massiv-barock-stil-art-6134/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/naehschatulle-schmuckschatulle-mit-geheimfaechern-mitte-19-jh-art-nr-6144/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/teewagen-eiche-um-1910-art-nr-6173/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/tuere-mit-geschnitztem-relief-darstellung-des-erzengel-gabriel-jungfrau-maria-mitte-19-jh-art-nr-6202/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/tuere-mit-geschnitztem-relief-geburt-christi-mitte-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/sonstiges/zillertaler-hochzeitstruhe-orig-fassung-um-1780-1800-art-nr-6194/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/biedermeier-spiegel-nussbaum-art-nr-4806/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/biedermeier-wandspiegel-nussbaum-sueddeutsch-1830-art-nr-6097/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/biedermeier-wandspiegel-nussbaum-um-1830-art-nr-6086/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/grosser-wandspiegel-biedermeier-klassizismus-applike-um-1800-pyramiden-mahagoni-art-nr-6131/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/grosser-wandspiegel-mit-plastischem-dekor-um-1880/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/grosser-wandspiegel-um-1800-anf-19-jh-art-nr-6052/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/jugendstil-wandspiegel-vergoldeter-rahmen-um-1900-art-nr-6116/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/louis-seize-wandspiegel-originale-vergoldung-um-1800/",
        "https://www.antiquitaeten-tuebingen.de/spiegel/wandspiegel-historismus-2-haelfte-19-jh-art-nr-6043/",
        "https://www.antiquitaeten-tuebingen.de/tische/art-nr-10278-louis-seize-konsoltisch-sueddeutsch-um-1800/",
        "https://www.antiquitaeten-tuebingen.de/tische/art-nr-6082-schmale-biedermeierkommode-um-1820/",
        "https://www.antiquitaeten-tuebingen.de/tische/art-nr-6122-schragentisch-mit-eingelegter-jagddarstellungen-alpenlaendisch-anfang-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/tische/art-nr-6132-beistelltisch-reich-intarsiert-aus-dem-osmanischen-reich-um-1900/",
        "https://www.antiquitaeten-tuebingen.de/tische/art-nr-6140-englischer-schreibtisch-mit-zwei-aufbauten-ende-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/tische/biedermeier-naehtisch-beistelltisch-art-3398/",
        "https://www.antiquitaeten-tuebingen.de/tische/biedermeier-wandkonsole-kirschbaum-sueddeutsch-1820-art-6113/",
        "https://www.antiquitaeten-tuebingen.de/tische/konsoltisch-barock-nussbaum-deutschland-mitte-18-jh-art-nr-10282/",
        "https://www.antiquitaeten-tuebingen.de/tische/rechteckiger-tisch-mit-messingplatte-im-niederlaendischen-barockstil-20-jh-art-6168/",
        "https://www.antiquitaeten-tuebingen.de/tische/wandkonsole-klassizismus-um-1800-art-nr-6208/",
        "https://www.antiquitaeten-tuebingen.de/tische/wandkonsole-mit-chinesen-verziert-2-haelfte-19-jh-art-6198/",
        "https://www.antiquitaeten-tuebingen.de/ueber-uns/",
        "https://www.antiquitaeten-tuebingen.de/uhren/art-nr-6071-empirependule-mit-darstellung-von-amor-anfang-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/uhren/art-nr-6127-bronzependule-mit-musizierendem-amor-feuervergoldet-frankreich-anf-19-jh/",
        "https://www.antiquitaeten-tuebingen.de/uhren/art-nr-6128-louis-xvi-kamingarnitur-mit-beistellern-von-le-roy-et-fils-paris/",
        "https://www.antiquitaeten-tuebingen.de/uhren/art-nr-6129-reisewecker-messinggehaeuse-um-1880/",
        "https://www.antiquitaeten-tuebingen.de/uhren/art-nr-6147-kaminuhr-im-klassizistischen-stil-um-1900/",
        "https://www.antiquitaeten-tuebingen.de/uhren/art-nr-6164-lenzkirchwecker-sogenannter-eulenwecker-um-1890/",
        "https://www.antiquitaeten-tuebingen.de/uhren/art-nr-6174-seltene-pendule-mit-schaukelndem-jungen-firma-lenzkirch-schwarzwald-1890/",
        "https://www.antiquitaeten-tuebingen.de/uhren/kaminuhr-zinkguss-um-1870-art-nr-6166/",
        "https://www.antiquitaeten-tuebingen.de/uhren/portaluhr-klassizismus-vergoldete-bronzen-um-1830-art-nr-6156/",
        "https://www.antiquitaeten-tuebingen.de/uhren/standuhr-england-mit-stundenschlag-um-1800/",
        "https://www.antiquitaeten-tuebingen.de/vitrinen/art-nr-5760-rokokovitrinenaufsatz-mit-drachenverzierung-um-1770/",
        "https://www.antiquitaeten-tuebingen.de/vitrinen/vitrine-louis-philippe-nussbaum-um-1870-art-nr-6161/",
        "https://www.apotheke-tuebingen.de/",
        "https://www.arbeitsagentur.de/vor-ort/reutlingen/tuebingen/",
        "https://www.arche-tuebingen.de/",
        "https://www.aspendos-tuebingen.de/",
        "https://www.asylzentrum-tuebingen.de/",
        "https://www.attac-tuebingen.de/",
        "https://www.attac.de/tuebingen/",
        "https://www.baupilot.com/universitaetsstadt-tuebingen/",
        "https://www.baupilot.com/universitaetsstadt-tuebingen/2-ausschreibungsrunde-obere-kreuzaecker-buehl-einf/",
        "https://www.bccn-tuebingen.de/",
        "https://www.bella-roma-tuebingen.de/",
        "https://www.bg-kliniken.de/klinik-tuebingen/",
        "https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/anaesthesie/termin/",
        "https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/hand-plastische-rekonstruktive-und-verbrennungschirurgie/termin/",
        "https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/notaufnahme/",
        "https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/querschnittzentrum/termin/",
        "https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/rehabilitation/",
        "https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/schmerzmedizin/termin/",
        "https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/unfall-und-wiederherstellungschirurgie/termin/",
        "https://www.bg-kliniken.de/klinik-tuebingen/karriere/",
        "https://www.bildungsspender.de/cvjm-tuebingen/",
        "https://www.biwakschachtel-tuebingen.de/",
        "https://www.biwakschachtel-tuebingen.de/app-faq/",
        "https://www.biwakschachtel-tuebingen.de/app/",
        "https://www.biwakschachtel-tuebingen.de/ausruestung/biwakschachtel-kollektion/",
        "https://www.biwakschachtel-tuebingen.de/bekleidung/frauen/kleider-roecke/",
        "https://www.biwakschachtel-tuebingen.de/datenschutzerklaerung-app/",
        "https://www.biwakschachtel-tuebingen.de/nutzungsbedingungen-app/",
        "https://www.biwakschachtel-tuebingen.de/rucksaecke/",
        "https://www.biwakschachtel-tuebingen.de/safety_sessions/",
        "https://www.biwakschachtel-tuebingen.de/schlafsaecke/",
        "https://www.biwakschachtel-tuebingen.de/schuhe/hallux-schuhe/",
        "https://www.biwakschachtel-tuebingen.de/teilnahmebedingungen/",
        "https://www.biwakschachtel-tuebingen.de/tickets/",
        "https://www.biwakschachtel-tuebingen.de/umweltpreis/",
        "https://www.biwakschachtel-tuebingen.de/zeltausstellung/",
        "https://www.biwe-bbq.de/ueber-uns/vor-ort/tuebingen/",
        "https://www.boje-tuebingen.de/",
        "https://www.bootsvermietung-tuebingen.de/",
        "https://www.botgarten.uni-tuebingen.de/",
        "https://www.boxenstop-tuebingen.de/",
        "https://www.boxenstop-tuebingen.de/agb/",
        "https://www.boxenstop-tuebingen.de/aktuelles/",
        "https://www.boxenstop-tuebingen.de/datenschutz/",
        "https://www.boxenstop-tuebingen.de/en.html"
        "https://www.boxenstop-tuebingen.de/impressum/",
        "https://www.boxenstop-tuebingen.de/kontakt-anfahrt/",
        "https://www.boxenstop-tuebingen.de/offnungszeiten-preise/",
        "https://www.boxenstop-tuebingen.de/reisen/",
        "https://www.boxenstop-tuebingen.de/veranstaltungen/",
        "https://www.boxenstop-tuebingen.de/vermietung-oldtimer-bus-und-hochzeitsauto/",
        "https://www.brueckenhaus-tuebingen.de/",
        "https://www.bsv-wuerttemberg.de/verband/bezirksgruppen/bg_reutlingen-tuebingen.php/",
        "https://www.buddhismus-tuebingen.de/",
        "https://www.buehler.de/lang/de/reisebuero-tuebingen/",
        "https://www.buendnis-fuer-familie-tuebingen.de/",
        "https://www.buendnis-fuer-familie-tuebingen.de/Hauptseite/",
        "https://www.buendnis-fuer-familie-tuebingen.de/Runder_Tisch_Kinderarmut/",
        "https://www.buergerstiftung-tuebingen.de/",
        "https://www.bueroaktiv-tuebingen.de/",
        "https://www.bueroaktiv-tuebingen.de/be-boerse/stadt-tuebingen/",
        "https://www.buntewiese-tuebingen.de/",
        "https://www.bwegt.de/land-und-leute/das-land-erleben/ausflugsziele/detail/landkreis-tourismus-baden-wuerttemberg/landkreis-tuebingen/93384a6c-60f1-49dd-9402-a36c596e2eef/",
        "https://www.career-service.uni-tuebingen.de/",
        "https://www.cccs.de/2019-02-28-cybervoting-tuebingen/",
        "https://www.chocolart.de/tuebingen/",
        "https://www.chocolat-tuebingen.de/",
        "https://www.cin.uni-tuebingen.de/",
        "https://www.cin.uni-tuebingen.de/home.php/",
        "https://www.cmfi.uni-tuebingen.de/",
        "https://www.cmfi.uni-tuebingen.de/en/",
        "https://www.collegium-tuebingen.de/",
        "https://www.concerto-vocale.uni-tuebingen.de/",
        "https://www.cpd-tuebingen.de.rs/",
        "https://www.curevac.com/1-international-mrna-health-conference-in-tuebingen-kuendigt-eine-neue-aera-in-der-modernen-medizin-an/",
        "https://www.curevac.com/curevac-ag-baut-mrna-wirkstoffproduktion-am-standort-tuebingen-aus-versorgung-klinischer-studien-und-spaetere-kommerzielle-verfuegbarkeit-der-curevac-produkte-gesichert/",
        "https://www.curevac.com/die-universitaet-tuebingen-verleiht-die-ehrensenatorenwuerde-an-dr-ingmar-hoerr-mitgruender-und-aufsichtsratsvorsitzenden-der-curevac-ag/",
        "https://www.curevac.com/moderne-waerme-im-cyber-valley-stadtwerke-tuebingen-versorgen-neues-produktionsgebaeude-von-curevac-gemeinsame-pressemitteilung/",
        "https://www.cvjm-tuebingen.de/",
        "https://www.cvjm-tuebingen.de/angebote/kinder/",
        "https://www.cvjm-tuebingen.de/freizeiten-und-veranstaltungen/",
        "https://www.cvjm-tuebingen.de/service/vermietung/stocherkahn/",
        "https://www.dachverband-tuebingen.de/",
        "https://www.dai-tuebingen.de/",
        "https://www.dai-tuebingen.de/ais_academy/2017/",
        "https://www.dai-tuebingen.de/ambassadors-in-sneakers-2018.html"
        "https://www.dai-tuebingen.de/berlin/",
        "https://www.dai-tuebingen.de/bibliothek/",
        "https://www.dai-tuebingen.de/bibliothek/ausleihe.html"
        "https://www.dai-tuebingen.de/bibliothek/eausleihe/",
        "https://www.dai-tuebingen.de/bibliothek/katalog/",
        "https://www.dai-tuebingen.de/bibliothek/kontakt.html"
        "https://www.dai-tuebingen.de/books/",
        "https://www.dai-tuebingen.de/booktok/",
        "https://www.dai-tuebingen.de/brass/",
        "https://www.dai-tuebingen.de/broschuere-anfordern.html"
        "https://www.dai-tuebingen.de/bundesfreiwilligendienst/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-01/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-02/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-03/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-04/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-05/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-06/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-07/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-08/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-09/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-10/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-11/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-12/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-13/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-14/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-15/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-16/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-17/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-18/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-19/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-20/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-21/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-22/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-23/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-24/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-25/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-26/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-27/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-28/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-29/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-30/",
        "https://www.dai-tuebingen.de/calendar-node-field-datum/day/2023-07-31/",
        "https://www.dai-tuebingen.de/daad/",
        "https://www.dai-tuebingen.de/das-dai.html"
        "https://www.dai-tuebingen.de/das-dai/das-dai-team.html"
        "https://www.dai-tuebingen.de/das-dai/mehr-info/usa-kontakte.html"
        "https://www.dai-tuebingen.de/das-dai/mitarbeit-raummiete/jobs.html"
        "https://www.dai-tuebingen.de/das-dai/mitarbeit-raummiete/raummiete.html"
        "https://www.dai-tuebingen.de/das-dai/mitarbeit-raummiete/volunteering.html"
        "https://www.dai-tuebingen.de/das-dai/mitglied-werden.html"
        "https://www.dai-tuebingen.de/das-dai/newsletter.html"
        "https://www.dai-tuebingen.de/das-dai/unsere-agb.html"
        "https://www.dai-tuebingen.de/datenschutz.html"
        "https://www.dai-tuebingen.de/ebooks/",
        "https://www.dai-tuebingen.de/en/about-the-institute/",
        "https://www.dai-tuebingen.de/en/advising/",
        "https://www.dai-tuebingen.de/en/advising/fairs/",
        "https://www.dai-tuebingen.de/en/advising/presentations/",
        "https://www.dai-tuebingen.de/en/becoming-a-teacher/",
        "https://www.dai-tuebingen.de/en/events/",
        "https://www.dai-tuebingen.de/en/events/podcasts/",
        "https://www.dai-tuebingen.de/en/events/podcasts/acrossthepond/",
        "https://www.dai-tuebingen.de/en/events/podcasts/meanwhileintuebingen/",
        "https://www.dai-tuebingen.de/en/events/podcasts/thequarantinediaries/",
        "https://www.dai-tuebingen.de/en/firmentrainings.html"
        "https://www.dai-tuebingen.de/en/high-school-students/",
        "https://www.dai-tuebingen.de/en/intercultural-projects/",
        "https://www.dai-tuebingen.de/en/intercultural-projects/ambassadors-in-sneakers.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/americans-of-tuebingen/",
        "https://www.dai-tuebingen.de/en/intercultural-projects/contact.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/contact/",
        "https://www.dai-tuebingen.de/en/intercultural-projects/dai-goes-hip-hop.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/past-projects/access.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/past-projects/english-youth-theater.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/past-projects/germany-year-1819.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/past-projects/high-school-exchange-2013-16.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/past-projects/sharing-views-2011.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/rent-an-american.html"
        "https://www.dai-tuebingen.de/en/intercultural-projects/rent-an-american/",
        "https://www.dai-tuebingen.de/en/intercultural-projects/rent-an-american/conversation-visits/",
        "https://www.dai-tuebingen.de/en/intercultural-projects/rent-an-american/presentation-visits/",
        "https://www.dai-tuebingen.de/en/intercultural-projects/rent-an-american/project-visits/",
        "https://www.dai-tuebingen.de/en/language-courses.html"
        "https://www.dai-tuebingen.de/en/language-courses/contact.html"
        "https://www.dai-tuebingen.de/en/language-courses/german-as-a-foreign-language.html"
        "https://www.dai-tuebingen.de/en/language-courses/language-tests.html"
        "https://www.dai-tuebingen.de/en/language-courses/translation-proofreading.html"
        "https://www.dai-tuebingen.de/en/languages-courses/",
        "https://www.dai-tuebingen.de/en/library.html"
        "https://www.dai-tuebingen.de/en/library/e-lending/",
        "https://www.dai-tuebingen.de/en/library/lending/",
        "https://www.dai-tuebingen.de/en/library/library-tours/",
        "https://www.dai-tuebingen.de/en/library/media-tips/50-states/",
        "https://www.dai-tuebingen.de/en/library/media-tips/blacklivesmatter/",
        "https://www.dai-tuebingen.de/en/library/media-tips/LGBT/",
        "https://www.dai-tuebingen.de/en/library/media-tips/politicsandsociety/",
        "https://www.dai-tuebingen.de/en/library/media-tips/womenshistorymonth/",
        "https://www.dai-tuebingen.de/en/node/2209/",
        "https://www.dai-tuebingen.de/en/node/2229/",
        "https://www.dai-tuebingen.de/en/other-dais/",
        "https://www.dai-tuebingen.de/en/our-terms-conditions.html"
        "https://www.dai-tuebingen.de/en/private-lessons.html"
        "https://www.dai-tuebingen.de/en/private-lessons/",
        "https://www.dai-tuebingen.de/en/students/",
        "https://www.dai-tuebingen.de/en/teacher/",
        "https://www.dai-tuebingen.de/en/the-dai-team/",
        "https://www.dai-tuebingen.de/en/the-dai/become-a-member.html"
        "https://www.dai-tuebingen.de/en/the-dai/executive-committee.html"
        "https://www.dai-tuebingen.de/en/the-dai/renting-rooms.html"
        "https://www.dai-tuebingen.de/en/the-dai/work-with-the-dai/internships.html"
        "https://www.dai-tuebingen.de/en/the-dai/work-with-the-dai/jobs.html"
        "https://www.dai-tuebingen.de/en/the-dai/work-with-the-dai/volunteering.html"
        "https://www.dai-tuebingen.de/en/travels-and-camps/",
        "https://www.dai-tuebingen.de/en/travels-and-camps/contact/",
        "https://www.dai-tuebingen.de/en/travels-and-camps/study-trips/",
        "https://www.dai-tuebingen.de/en/travels-and-camps/youth-camps/",
        "https://www.dai-tuebingen.de/en/travels-and-camps/youth-trips/",
        "https://www.dai-tuebingen.de/en/travels-camps/",
        "https://www.dai-tuebingen.de/en/united-states/",
        "https://www.dai-tuebingen.de/en/usa-advising.html"
        "https://www.dai-tuebingen.de/en/usa-advising/appointments/",
        "https://www.dai-tuebingen.de/en/usa-advising/contact/",
        "https://www.dai-tuebingen.de/en/welcome_desk/",
        "https://www.dai-tuebingen.de/escape/",
        "https://www.dai-tuebingen.de/event-kalender.html"
        "https://www.dai-tuebingen.de/events/kids-story-time.html-22/",
        "https://www.dai-tuebingen.de/flo�/",
        "https://www.dai-tuebingen.de/gaming/",
        "https://www.dai-tuebingen.de/get-in-touch.html"
        "https://www.dai-tuebingen.de/hill/",
        "https://www.dai-tuebingen.de/hiphop.html"
        "https://www.dai-tuebingen.de/impressum.html"
        "https://www.dai-tuebingen.de/Israel_2023/",
        "https://www.dai-tuebingen.de/lehrkraefte.html"
        "https://www.dai-tuebingen.de/midterms/",
        "https://www.dai-tuebingen.de/newsletter-bibliothek/",
        "https://www.dai-tuebingen.de/node/2073/",
        "https://www.dai-tuebingen.de/node/2182/",
        "https://www.dai-tuebingen.de/node/2183/",
        "https://www.dai-tuebingen.de/node/2184/",
        "https://www.dai-tuebingen.de/node/2224/",
        "https://www.dai-tuebingen.de/node/2310/",
        "https://www.dai-tuebingen.de/node/2429/",
        "https://www.dai-tuebingen.de/node/2643/",
        "https://www.dai-tuebingen.de/node/2789/",
        "https://www.dai-tuebingen.de/nyc2023/",
        "https://www.dai-tuebingen.de/praktika.html"
        "https://www.dai-tuebingen.de/previously-on/",
        "https://www.dai-tuebingen.de/previously-on/abtreibung-in-den-usa/",
        "https://www.dai-tuebingen.de/previously-on/athlete-a/",
        "https://www.dai-tuebingen.de/previously-on/bombshell/",
        "https://www.dai-tuebingen.de/previously-on/brooklyn-99/",
        "https://www.dai-tuebingen.de/previously-on/chicago-7/",
        "https://www.dai-tuebingen.de/previously-on/coco/",
        "https://www.dai-tuebingen.de/previously-on/coded-bias/",
        "https://www.dai-tuebingen.de/previously-on/community/",
        "https://www.dai-tuebingen.de/previously-on/crazy-exgirlfriend/",
        "https://www.dai-tuebingen.de/previously-on/dolly-parton/",
        "https://www.dai-tuebingen.de/previously-on/finale/",
        "https://www.dai-tuebingen.de/previously-on/frischer-wind-im-kongress/",
        "https://www.dai-tuebingen.de/previously-on/hallmark-movies/",
        "https://www.dai-tuebingen.de/previously-on/jeffrey-epstein-stinkreich/",
        "https://www.dai-tuebingen.de/previously-on/latenight/",
        "https://www.dai-tuebingen.de/previously-on/LGBTQ-Dokumentationen/",
        "https://www.dai-tuebingen.de/previously-on/mamma-mia/",
        "https://www.dai-tuebingen.de/previously-on/megamind/",
        "https://www.dai-tuebingen.de/previously-on/one-day-at-a-time/",
        "https://www.dai-tuebingen.de/previously-on/pushing-daisies/",
        "https://www.dai-tuebingen.de/previously-on/santa-clarita-diet/",
        "https://www.dai-tuebingen.de/previously-on/sei-lieb/",
        "https://www.dai-tuebingen.de/previously-on/sense-8/",
        "https://www.dai-tuebingen.de/previously-on/the-farewell/",
        "https://www.dai-tuebingen.de/previously-on/the-good-place/",
        "https://www.dai-tuebingen.de/previously-on/unter-dem-tellerrand/",
        "https://www.dai-tuebingen.de/previously-on/weihnachtsfolgen/",
        "https://www.dai-tuebingen.de/previously-on/zurueck-in-die-zukunft/",
        "https://www.dai-tuebingen.de/projekte/",
        "https://www.dai-tuebingen.de/projekte/access.html"
        "https://www.dai-tuebingen.de/projekte/ambassadors-in-sneakers.html"
        "https://www.dai-tuebingen.de/projekte/ambassadors-in-sneakers.html /",
        "https://www.dai-tuebingen.de/projekte/ambassadors-in-sneakers/ambassadors-in-sneakers-2019.html"
        "https://www.dai-tuebingen.de/projekte/ambassadors-in-sneakers/ambassadors-in-sneakers-2022/",
        "https://www.dai-tuebingen.de/projekte/americans-of-tuebingen/",
        "https://www.dai-tuebingen.de/projekte/citizen-diplomat.html"
        "https://www.dai-tuebingen.de/projekte/deutschlandjahr-2018-2019/podcast-meanwhile-in-tuebingen.html"
        "https://www.dai-tuebingen.de/projekte/deutschlandjahr-201819.html"
        "https://www.dai-tuebingen.de/projekte/english-youth-theater.html"
        "https://www.dai-tuebingen.de/projekte/going-green.html"
        "https://www.dai-tuebingen.de/projekte/high-school-exchange-2013-16.html"
        "https://www.dai-tuebingen.de/projekte/kontakt-projektabteilung.html"
        "https://www.dai-tuebingen.de/projekte/rent-an-american.html"
        "https://www.dai-tuebingen.de/projekte/rent-an-american.html /",
        "https://www.dai-tuebingen.de/projekte/rent-an-american/conversation-visits.html"
        "https://www.dai-tuebingen.de/projekte/rent-an-american/presentation-visits.html"
        "https://www.dai-tuebingen.de/projekte/rent-an-american/project-visits.html"
        "https://www.dai-tuebingen.de/projekte/sharing-views-2011.html"
        "https://www.dai-tuebingen.de/raa/anmeldung/",
        "https://www.dai-tuebingen.de/reisen-camps.html"
        "https://www.dai-tuebingen.de/reisen-camps/beratung-und-information.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/adventure-camp.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/american-sports-camp.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/americansummercamp/",
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/cheer-camp.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/coding-camp/",
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/dance-move-camp.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/kids-camp.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/musical-theater-camp.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendcamps/us-sports-camp.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendreisen.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendreisen/sprachreise-abi-und-dann.html"
        "https://www.dai-tuebingen.de/reisen-camps/jugendreisen/sprachreise-san-diego.html"
        "https://www.dai-tuebingen.de/reisen-camps/newsletter-reisen.html"
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen.html"
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/august-2017-westward-bound.html"
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/juli-2019-explore-the-american-southwest.html"
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/musikreise-new-orleans.html"
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/nyc2023/",
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/nyc21/",
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/oktober-2019-studienreise-israel.html-0/",
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/oktober-2020-studienreise-washington-dc.html"
        "https://www.dai-tuebingen.de/reisen-camps/studienreisen-und-lehrerfortbildungen/studienreise-washington-dc.html"
        "https://www.dai-tuebingen.de/rueckenwind/",
        "https://www.dai-tuebingen.de/sandiego2023/",
        "https://www.dai-tuebingen.de/schoolnewsletter.html"
        "https://www.dai-tuebingen.de/schuelerinnen.html"
        "https://www.dai-tuebingen.de/selbsteinstufungstest-englisch.html"
        "https://www.dai-tuebingen.de/shop/",
        "https://www.dai-tuebingen.de/sites/default/files/uploads/allgemein/Presse/swr4_beitrag_erstwaehlerin_kim_schafhauser.mp3/",
        "https://www.dai-tuebingen.de/sites/default/files/uploads/allgemein/Presse/swr4_portrait_lucas_ogden.mp3/",
        "https://www.dai-tuebingen.de/snackavaganza/",
        "https://www.dai-tuebingen.de/sommernacht/",
        "https://www.dai-tuebingen.de/spenden/",
        "https://www.dai-tuebingen.de/sprachkurse.html"
        "https://www.dai-tuebingen.de/sprachkurse/am-dai-unterrichten.html"
        "https://www.dai-tuebingen.de/sprachkurse/deutsch-als-fremdsprache-daf.html"
        "https://www.dai-tuebingen.de/sprachkurse/englischkurse.html"
        "https://www.dai-tuebingen.de/sprachkurse/firmentrainings.html"
        "https://www.dai-tuebingen.de/sprachkurse/gymglish/",
        "https://www.dai-tuebingen.de/sprachkurse/privatunterricht.html"
        "https://www.dai-tuebingen.de/sprachkurse/sprachtests.html"
        "https://www.dai-tuebingen.de/sprachkurse/uebersetzungen-korrekturauftraege.html"
        "https://www.dai-tuebingen.de/sprachtests.html"
        "https://www.dai-tuebingen.de/studierende.html"
        "https://www.dai-tuebingen.de/tiktok/",
        "https://www.dai-tuebingen.de/usa-beratung.html"
        "https://www.dai-tuebingen.de/usa-beratung/",
        "https://www.dai-tuebingen.de/usa-beratung/anmeldung.html"
        "https://www.dai-tuebingen.de/usa-beratung/au-pair/usa.html"
        "https://www.dai-tuebingen.de/usa-beratung/downunder/",
        "https://www.dai-tuebingen.de/usa-beratung/finanzierung/fsj/",
        "https://www.dai-tuebingen.de/usa-beratung/finanzierung/highschool/",
        "https://www.dai-tuebingen.de/usa-beratung/finanzierung/studium-degree-seeking/",
        "https://www.dai-tuebingen.de/usa-beratung/finanzierung/studium-semester/",
        "https://www.dai-tuebingen.de/usa-beratung/freiwilligendienste/freiwilligendienste-in-den-usa.html"
        "https://www.dai-tuebingen.de/usa-beratung/highschool.html"
        "https://www.dai-tuebingen.de/usa-beratung/kanada/",
        "https://www.dai-tuebingen.de/usa-beratung/kontakt.html"
        "https://www.dai-tuebingen.de/usa-beratung/material/",
        "https://www.dai-tuebingen.de/usa-beratung/messe/",
        "https://www.dai-tuebingen.de/usa-beratung/praktikum/usa.html"
        "https://www.dai-tuebingen.de/usa-beratung/studium.html"
        "https://www.dai-tuebingen.de/usa-beratung/usa/",
        "https://www.dai-tuebingen.de/usa-beratung/usa/campcounselor/",
        "https://www.dai-tuebingen.de/usa-beratung/usa/kurzzeitprogramme/",
        "https://www.dai-tuebingen.de/usa-beratung/vortrag/",
        "https://www.dai-tuebingen.de/usa-beratung/work-travel/usa.html"
        "https://www.dai-tuebingen.de/usa-kontakte/tuebingen-progressive-americans.html"
        "https://www.dai-tuebingen.de/veranstaltungen.html"
        "https://www.dai-tuebingen.de/veranstaltungen/ausstellungen.html"
        "https://www.dai-tuebingen.de/veranstaltungen/coping-with-covid/",
        "https://www.dai-tuebingen.de/veranstaltungen/dai-junior/",
        "https://www.dai-tuebingen.de/veranstaltungen/event-kalender.html"
        "https://www.dai-tuebingen.de/veranstaltungen/filme.html"
        "https://www.dai-tuebingen.de/veranstaltungen/podcasts/",
        "https://www.dai-tuebingen.de/veranstaltungen/podcasts/acrossthepond/",
        "https://www.dai-tuebingen.de/veranstaltungen/podcasts/thequarantinediaries/",
        "https://www.das-kriminal-dinner.de/krimidinner-tatorte/tuebingen/japengo/",
        "https://www.dav-tuebingen.de.stage.esono.net/service/ausruestungsverleih/ausruestungsverleih-fuer-mitglieder_aid_1191.html"
        "https://www.dav-tuebingen.de/",
        "https://www.dav-tuebingen.de/ausruestung/grundausruestung_aid_207.html"
        "https://www.dav-tuebingen.de/dummy-gruppe/keine-kategorie-gesetzt/satzung-fuer-die-sektion-tuebingen-des-deutschen-alpenvereins_aid_199.html"
        "https://www.dav-tuebingen.de/home/news/interview-mehr-zu-outdoorent_aid_1160.html"
        "https://www.dav-tuebingen.de/jugend-familie/bericht-jugend-ein-oertchen-fuer-die-jugend_aid_1398.html"
        "https://www.dav-tuebingen.de/jugend-familie/jdav-tuebingen-besetzung-und-aufgaben-der-referate-im-jugendbereich_aid_948.html"
        "https://www.dav-tuebingen.de/sektion/ansprechpartner/matthias-lustig_aid_423.html"
        "https://www.dav-tuebingen.de/sektion/geschaeftsstelle/geschaeftsstelle_aid_204.html"
        "https://www.dav-tuebingen.de/Sektion/Vereinsmitarbeit/Das-Ehrenamt/",
        "https://www.dav-tuebingen.de/Veranstaltungsprogramm/",
        "https://www.diakonisches-institut.de/index.php/tuebingen/",
        "https://www.diekleinenzwergetuebingen.de/",
        "https://www.dktk-dkfz.de/en/sites/tuebingen/",
        "https://www.doctolib.de/gemeinschaftspraxis/tuebingen/orthopaedisches-chirurgisches-centrum-tuebingen /",
        "https://www.drk-tuebingen.de/",
        "https://www.drk-tuebingen.de/footer-menue-deutsch/service/datenschutz.html"
        "https://www.dzd-ev.de/das-dzd/standorte/uni-tuebingen/",
        "https://www.dzd-ev.de/das-dzd/standorte/uni-tuebingen/index.html"
        "https://www.dzd-ev.de/en/the-dzd/locations/uni-tuebingen/index.html"
        "https://www.dzif.de/de/standorte/tuebingen/",
        "https://www.dzif.de/en/about_us/partner_sites/tuebingen/",
        "https://www.dzne.de/en/about-us/sites/tuebingen/",
        "https://www.dzne.de/ueber-uns/standorte/tuebingen/",
        "https://www.eb.tuebingen.mpg.de/",
        "https://www.eb.tuebingen.mpg.de/de/",
        "https://www.eb.tuebingen.mpg.de/open-positions.html"
        "https://www.ebike-tuebingen.de/",
        "https://www.eltern-gss-tuebingen.de/",
        "https://www.emk-tuebingen.de/",
        "https://www.engagiert-im-kreis-tuebingen.de/",
        "https://www.escience.uni-tuebingen.de/",
        "https://www.esg-tuebingen.de/",
        "https://www.esg-tuebingen.de/meta/datenschutz/",
        "https://www.euronics.de/tuebingen-betz/",
        "https://www.ev-stephanusgemeinde-tuebingen.de/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/cms/startseite/kirchengemeinden/studierendengemeinde/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/kindergaerten/eberhardskindergarten/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/kindergaerten/frida-wetzel-kindergarten-im-stephanuszentrum/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/kindergaerten/kindergarten-im-rotbad/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/kindergaerten/kindergarten-rappstrasse/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/kindergaerten/kindergarten-waldhaeuser-ost/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/kindergaerten/martinskindergarten/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/kirchenmusik/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/meta/datenschutz/",
        "https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/spenden/tuebinger-beitrag/",
        "https://www.evangelischer-kirchenbezirk-tuebingen.de/",
        "https://www.eye-tuebingen.de/berens/",
        "https://www.fa-tuebingen.de/",
        "https://www.facebook.com/biwakschachtel.tuebingen/",
        "https://www.facebook.com/cvjm.tuebingen/",
        "https://www.facebook.com/davtuebingen/",
        "https://www.facebook.com/elsatuebingen/",
        "https://www.facebook.com/esszimmer.tuebingen/",
        "https://www.facebook.com/feuerwehr.tuebingen/",
        "https://www.facebook.com/floorballtuebingen/",
        "https://www.facebook.com/gjtuebingen/",
        "https://www.facebook.com/gruenetuebingen/",
        "https://www.facebook.com/gw.tuebingen/",
        "https://www.facebook.com/hecht.einrichtungen.tuebingen/",
        "https://www.facebook.com/hotelamschloss.tuebingen/",
        "https://www.facebook.com/jgr.tuebingen/",
        "https://www.facebook.com/kathrinschustertuebingen/",
        "https://www.facebook.com/kreistuebingen/",
        "https://www.facebook.com/lamedinatuebingen/",
        "https://www.facebook.com/littleindiatuebingen/",
        "https://www.facebook.com/medsports.tuebingen/",
        "https://www.facebook.com/nikolauslauftuebingen/",
        "https://www.facebook.com/rptuebingen/posts/pfbid02gpCwj8SAZHbeFAVMWgsaiUrawpzz9XzP3fioVchDqTme17oKSYxFBQRsC8mTzBdnl/",
        "https://www.facebook.com/rptuebingen/posts/pfbid056VVPk1epQev4Ave7PhEr91fo7q5ocKA4xBgXQwZUhEvy5RhsHjbQCRV1YEgFhBGl/",
        "https://www.facebook.com/rptuebingen/posts/pfbid0JYb1APxXSCYvPQD9AV59ZJiZptnSW7BJkViDxebhFjmfTTAkP3qApEygo4LWQBPbl/",
        "https://www.facebook.com/slowfoodtuebingen/",
        "https://www.facebook.com/stadtwerketuebingen/",
        "https://www.facebook.com/tsgtuebingen/",
        "https://www.facebook.com/tuebingen.de/",
        "https://www.facebook.com/tuebingen.info/",
        "https://www.facebook.com/uniklinikum.tuebingen/",
        "https://www.facebook.com/unituebingen/",
        "https://www.facebook.com/vhstuebingen/",
        "https://www.facebook.com/yogalofttuebingen/",
        "https://www.fahrradladen-tuebingen.de/",
        "https://www.faltrad-tuebingen.de/",
        "https://www.faros-tuebingen.com/",
        "https://www.faros-tuebingen.com/agb/",
        "https://www.faros-tuebingen.com/datenschutz/",
        "https://www.faros-tuebingen.com/impressum/",
        "https://www.faros-tuebingen.com/reservierung/",
        "https://www.faros-tuebingen.com/speisekarte/",
        "https://www.faros-tuebingen.com/�ber-uns/",
        "https://www.fatk.uni-tuebingen.de/",
        "https://www.faz.net/aktuell/feuilleton/buecher/ingeborg-bachmann-preis-2023-valeria-gordeev-aus-tuebingen-gewinnt-19005059.html"
        "https://www.faz.net/aktuell/feuilleton/kunst-und-architektur/maler-daniel-richter-in-tuebingen-mit-punk-historiengemaelden-18929606.html"
        "https://www.faz.net/aktuell/feuilleton/thema/tuebingen-p2/",
        "https://www.faz.net/aktuell/feuilleton/thema/tuebingen-p3/",
        "https://www.faz.net/aktuell/feuilleton/thema/tuebingen-p4/",
        "https://www.faz.net/aktuell/feuilleton/thema/tuebingen-p5/",
        "https://www.faz.net/aktuell/gesellschaft/freiheit-durch-freitesten-so-geht-tuebingen-mit-der-pandemie-um-17269091.html"
        "https://www.faz.net/aktuell/gesellschaft/kriminalitaet/urteil-in-tuebingen-tochter-zu-sex-dates-mitgenommen-haftstrafen-fuer-paar-18997361.html"
        "https://www.faz.net/aktuell/politik/boris-palmer-in-tuebingen-wiedergewaehlt-eine-ohrfeige-fuer-die-gruenen-18409836.html"
        "https://www.faz.net/aktuell/politik/inland/boris-palmer-bleibt-oberbuergermeister-von-tuebingen-ein-wahlgang-genuegt-18409084.html"
        "https://www.faz.net/aktuell/politik/inland/boris-palmer-oberbuergermeister-tuebingens-tritt-bei-den-gruenen-aus-18861593.html"
        "https://www.faz.net/aktuell/politik/inland/boris-palmer-wie-die-gruenen-ueber-tuebingens-oberbuergermeister-denken-18864079.html"
        "https://www.faz.net/aktuell/politik/inland/buergermeisterwahl-in-tuebingen-stadt-sucht-oberhaupt-18400916.html"
        "https://www.faz.net/aktuell/politik/inland/palmer-in-tuebingen-ansporn-fuer-die-cdu-menetekel-fuer-die-gruenen-18421195.html"
        "https://www.faz.net/aktuell/wirtschaft/unternehmen/shoppen-in-tuebingen-mit-schnelltest-17246649.html"
        "https://www.fbs-tuebingen.de/",
        "https://www.feg-tuebingen.de/",
        "https://www.feuerwehr-tuebingen.de/",
        "https://www.ff-stadtmuseum-tuebingen.de/",
        "https://www.figurentheater-tuebingen.de/",
        "https://www.filmtage-tuebingen.de/",
        "https://www.filmtage-tuebingen.de/latino/",
        "https://www.filmtage-tuebingen.de/latino/index.htm/",
        "https://www.flixbus.com/bus/tubingen/",
        "https://www.fml.tuebingen.mpg.de/",
        "https://www.fml.tuebingen.mpg.de/fml/",
        "https://www.franzosen-tuebingen.de/",
        "https://www.franzwerk-tuebingen.de/",
        "https://www.frauen-helfen-frauen-tuebingen.de/russkii/",
        "https://www.frauenfilmtagetuebingen.de/",
        "https://www.fridaysforfuturetuebingen.de/",
        "https://www.friedensplenum-tuebingen.de/",
        "https://www.galli-tuebingen.de/",
        "https://www.gastroguide.de/restaurant/106013/doener-kalender/tuebingen/",
        "https://www.gastroguide.de/restaurant/106467/salam-arabische-spezialitaeten/tuebingen/",
        "https://www.gastroguide.de/restaurant/106467/salam-arabische-spezialitaeten/tuebingen/bewertung/19997/",
        "https://www.gastroguide.de/restaurant/1184/schwaerzlocher-hof/tuebingen/",
        "https://www.gastroguide.de/restaurant/142214/pizzeria-unckel/tuebingen/",
        "https://www.gastroguide.de/restaurant/142216/wok-in/tuebingen/",
        "https://www.gastroguide.de/restaurant/142216/wok-in/tuebingen/bewertung/15100/",
        "https://www.gastroguide.de/restaurant/159690/gasthausbrauerei-neckarmueller/tuebingen/",
        "https://www.gastroguide.de/restaurant/180921/hao-s-box/tuebingen/",
        "https://www.gastroguide.de/restaurant/180921/hao-s-box/tuebingen/bewertung/19610/",
        "https://www.gastroguide.de/restaurant/192187/cafe-lieb/tuebingen/",
        "https://www.gastroguide.de/restaurant/192187/cafe-lieb/tuebingen/bewertung/8282/",
        "https://www.gastroguide.de/restaurant/192261/padeffke-baeckerei/tuebingen/",
        "https://www.gastroguide.de/restaurant/192261/padeffke-baeckerei/tuebingen/bewertung/12975/",
        "https://www.gastroguide.de/restaurant/200545/manufaktur/tuebingen/",
        "https://www.gastroguide.de/restaurant/200545/manufaktur/tuebingen/bewertung/12124/",
        "https://www.gastroguide.de/restaurant/201953/haupt-bahnhof-tuebingen-gastronomie-kultur/tuebingen/",
        "https://www.gastroguide.de/restaurant/201953/haupt-bahnhof-tuebingen-gastronomie-kultur/tuebingen/bewertung/12972/",
        "https://www.gastroguide.de/restaurant/206929/gauker/tuebingen/",
        "https://www.gastroguide.de/restaurant/206929/gauker/tuebingen/bewertung/15115/",
        "https://www.gastroguide.de/restaurant/206939/snack-house/tuebingen/",
        "https://www.gastroguide.de/restaurant/206939/snack-house/tuebingen/bewertung/15187/",
        "https://www.gastroguide.de/restaurant/207495/ristorante-da-angelo/tuebingen/",
        "https://www.gastroguide.de/restaurant/207495/ristorante-da-angelo/tuebingen/bewertung/15395/",
        "https://www.gastroguide.de/restaurant/207496/pizza-pasta-wir-bringens-pizzaservice/tuebingen/",
        "https://www.gastroguide.de/restaurant/207496/pizza-pasta-wir-bringens-pizzaservice/tuebingen/bewertung/15402/",
        "https://www.gastroguide.de/restaurant/219322/asien-haus/tuebingen/",
        "https://www.gastroguide.de/restaurant/219322/asien-haus/tuebingen/bewertung/21281/",
        "https://www.gastroguide.de/restaurant/222126/sportgaststaette-derendingen/tuebingen/",
        "https://www.gastroguide.de/restaurant/48768/chin-thai-wok/tuebingen/",
        "https://www.gastroguide.de/restaurant/48768/chin-thai-wok/tuebingen/bewertung/15103/",
        "https://www.gastroguide.de/restaurant/5178/restaurant-istanbul/tuebingen/",
        "https://www.gastroguide.de/restaurant/5178/restaurant-istanbul/tuebingen/bewertung/8092/",
        "https://www.gastroguide.de/restaurant/5786/kichererbse/tuebingen/",
        "https://www.gastroguide.de/restaurant/5786/kichererbse/tuebingen/bewertung/6855/",
        "https://www.gastroguide.de/restaurant/60667/marquardtei/tuebingen/",
        "https://www.gastroguide.de/restaurant/60667/marquardtei/tuebingen/bewertung/7433/",
        "https://www.gastroguide.de/restaurant/77118/reithausgaststaette/tuebingen/",
        "https://www.gastroguide.de/restaurant/89751/krumme-bruecke/tuebingen/",
        "https://www.gaus-architekten.de/de/projekte/oeffentlich/feuerwehrgeraetehaus-in-tuebingen-lustnau/",
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-bericht-usa-wollen-sich-t%C3%BCbinger-impfstoff-gegen-das-coronavirus-sichern-_arid,6241331.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-curevac-investor-kein-exklusivvertrag-f%C3%BCr-corona-impfstoff-f%C3%BCr-usa-_arid,6241538.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-gomaringer-stimmen-in-zeiten-des-virus-ab-_arid,6243389.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-grundlagen-f%C3%BCr-schutzanz%C3%BCge-_arid,6244061.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-helfer-aus-der-m%C3%B6ssinger-nachbarschaft-_arid,6243953.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-linke-fraktion-im-t%C3%BCbinger-gemeinderat-fordert-zivilklausel-f%C3%BCr-curevac-_arid,6241379.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-nachtleben-in-zeiten-von-corona-ein-streifzug-durch-t%C3%BCbingen-_arid,6241454.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-streit-um-t%C3%BCbinger-impfstoff-firma-erreicht-kreis-der-g7-staaten-_arid,6242021.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-t%C3%BCbinger-impfstoff-firma-kein-angebot-von-donald-trump-_arid,6241907.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-t%C3%BCbinger-landtagsabgeordneter-daniel-lede-abalsoforthilfen-f%C3%BCr-selbst%C3%A4ndige-und-unternehmen-kommen-_arid,6244028.html"
        "https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-t%C3%BCbinger-tafel-erkl%C3%A4rt-wieso-sie-schlie%C3%9Fen-muss-_arid,6241727.html"
        "https://www.gebrauchtwarenboerse-tuebingen.de/",
        "https://www.geburtshaus-tuebingen.de/",
        "https://www.gelbeseiten.de/hebammen/tuebingen/",
        "https://www.gelbeseiten.de/taxi/tuebingen/",
        "https://www.gemeinde.tuebingen-stiftskirche.elk-wue.de/meta/datenschutz/",
        "https://www.geschichtswerkstatt-tuebingen.de/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/80-jahre-deportation-nach-theresienstadt/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/der-swr-berichtet-ueber-den-juedischen-friedhof-von-wankheim/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/die-geschichtswerkstatt-tuebingen-und-das-karl-von-frisch-gymnasium-dusslingen-vereinbaren-eine-bildungspartnerschaft/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/filmemacher-julian-riek-beim-freien-radio-wueste-welle/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/filmpremiere-tuebingen-im-nationalsozialismus/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/fuehrungen-fuer-das-berufliche-gymnasium-sigmaringen/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/lucius-teidelbaum-auf-radio-wueste-welle/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/neue-kurzbiografie-www-ns-akteure-in-tuebingen-de/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/neue-kurzbiografien-auf-www-ns-akteure-in-tuebingen-de/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/blog/prof-dr-karen-glinert-carlson-in-tuebingen/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/fuehrungen/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/veranstaltungen/",
        "https://www.geschichtswerkstatt-tuebingen.de/aktuelles/veranstaltungsarchiv/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/bibliothek-archiv-der-geschichtswerkstatt/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/fuehrungen/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/fuehrungen/fuehrungen-der-jungen-geschichtswerktatt/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/fuehrungen/geschichtspfad-zum-nationalsozialismus/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/fuer-schulen/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/fuer-schulen/bildungsmaterialien/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/fuer-schulen/schulmodul/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/das-juedische-zwangsaltenheim-eschenau-und-seine-bewohner/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/juedische-spuren-in-tuebingen/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/ploetzlich-war-alles-anders-jugend-im-nationalsozialistischen-tuebingen/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/simon-hayum-erinnerungen-aus-dem-exil/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/vom-braunen-hemd-zur-weissen-weste/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/wege-der-tuebinger-juden/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/zerstoerte-demokratie/",
        "https://www.geschichtswerkstatt-tuebingen.de/angebote/veroeffentlichungen/zerstoerte-hoffnungen/",
        "https://www.geschichtswerkstatt-tuebingen.de/datenschutz/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/junge-geschichtswerkstatt/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/kontakt/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/kooperationen/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/links/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/ueber-uns/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/unterstuetzen-sie-uns/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/unterstuetzen-sie-uns/mitglied-werden/",
        "https://www.geschichtswerkstatt-tuebingen.de/die-geschichtswerkstatt/unterstuetzen-sie-uns/spenden/",
        "https://www.geschichtswerkstatt-tuebingen.de/en/",
        "https://www.geschichtswerkstatt-tuebingen.de/impressum/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/arbeitskreis-familie-hirsch/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/begegnungen/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/denkmal-synagogenplatz/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/geschichtspfad-zum-nationalsozialismus/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/grabert-ein-extrem-rechter-verlag/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/juedische-familien-im-suedwesten/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/ns-akteure-in-tuebingen/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/projekte-der-jungen-geschichtswerkstatt/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/projekte-der-jungen-geschichtswerkstatt/erinnerung-an-sinti-und-roma/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/projekte-der-jungen-geschichtswerkstatt/online-ausstellung-kinder-aus-dem-suedwesten-im-holocaust/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/projekte-der-jungen-geschichtswerkstatt/pieces-of-memory-children-in-the-shoah-and-us/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/taeterinnen-ein-stueck-ueber-brave-maedels-und-nazi-omas/",
        "https://www.geschichtswerkstatt-tuebingen.de/projekte/zeitzeugenprojekt/",
        "https://www.gj-tuebingen.de/",
        "https://www.greenguide-tuebingen.de/",
        "https://www.gruene-tuebingen.de/partei/stadtverband-tuebingen/expand/757597/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/partei/stadtverband-tuebingen/expand/758134/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/partei/stadtverband-tuebingen/expand/790732/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/partei/stadtverband-tuebingen/expand/801131/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/partei/stadtverband-tuebingen/stadtvorstand/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/588627/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/588628/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/588629/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/620981/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/629161/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/634647/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/652999/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/666250/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/739244/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/bundesparteitage/expand/813643/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/gruenes-kino/expand/620974/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/gruenes-kino/expand/620975/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/gruenes-kino/expand/638666/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/gruenes-kino/expand/649056/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/gruenes-sofa/expand/591300/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/gruenes-sofa/expand/625454/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/gruenes-sofa/expand/625456/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/kreismitgliederversammlung/expand/588615/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/kreismitgliederversammlung/expand/649599/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/landesparteitage/expand/588625/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/landesparteitage/expand/588626/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/landesparteitage/expand/591298/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/landesparteitage/expand/636137/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/landesparteitage/expand/636141/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/landesparteitage/expand/666345/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/landesparteitage/expand/787771/nc/1/dn/1/",
        "https://www.gruene-tuebingen.de/veranstaltungen/lesungen/expand/729546/nc/1/dn/1/",
        "https://www.gss-tuebingen.de/",
        "https://www.gwg-tuebingen.de/",
        "https://www.gwg-tuebingen.de/80/",
        "https://www.gwg-tuebingen.de/news/artikel/projekt-palazzo/",
        "https://www.gzt-tuebingen.de/",
        "https://www.hanse-tuebingen.de/",
        "https://www.hausundgrund-tuebingen.de/",
        "https://www.hci.uni-tuebingen.de/chair/team/enkelejda-kasneci/",
        "https://www.hgv-tuebingen.de/",
        "https://www.hgv-tuebingen.de/13-abendspaziergang-11-mai-2023/",
        "https://www.hgv-tuebingen.de/abenspaziergang/",
        "https://www.hgv-tuebingen.de/aktuelles/",
        "https://www.hgv-tuebingen.de/author/selcuk26/",
        "https://www.hgv-tuebingen.de/category/allgemein/",
        "https://www.hgv-tuebingen.de/chocolart/",
        "https://www.hgv-tuebingen.de/cookie-richtlinie-eu/",
        "https://www.hgv-tuebingen.de/digitalisierung/",
        "https://www.hgv-tuebingen.de/geschaeftsstelle/",
        "https://www.hgv-tuebingen.de/hgv-fruehjahrsempfang-am-16-mai-2023/",
        "https://www.hgv-tuebingen.de/impulse-des-hgv-fuer-tuebingen/",
        "https://www.hgv-tuebingen.de/kontakt/",
        "https://www.hgv-tuebingen.de/membership-login/",
        "https://www.hgv-tuebingen.de/membership-login/password-reset/",
        "https://www.hgv-tuebingen.de/mitglied-werden/",
        "https://www.hgv-tuebingen.de/stellungnahme-des-hgv-zur-eroeffnung-des-amazon-forschungszentrums/",
        "https://www.hgv-tuebingen.de/stellungnahme-zu-rainer-imms-uebrigens-im-tagblatt-vom-13-04-2023/",
        "https://www.hgv-tuebingen.de/tuebingen-erleben-broschuere/",
        "https://www.hgv-tuebingen.de/tuebinger-gutschein/",
        "https://www.hgv-tuebingen.de/veranstaltungen-bilder-2023/",
        "https://www.hgv-tuebingen.de/veranstaltungen/",
        "https://www.hgv-tuebingen.de/vision-concept-store-eroeffnung-am-28-03-2023/",
        "https://www.hgv-tuebingen.de/vorstand/",
        "https://www.hgv-tuebingen.de/was-wir-bieten/",
        "https://www.hih-tuebingen.de/",
        "https://www.hih-tuebingen.de/de/forschung/unabhaengige-forschungsgruppen/",
        "https://www.hih-tuebingen.de/de/forschung/unabhaengige-forschungsgruppen/translationale-bildgebung-kortikaler-mikrostruktur/",
        "https://www.hih-tuebingen.de/de/forschung/vaskulaere-neurologie/forschungsgruppen/neuroplastizitaet/",
        "https://www.hih-tuebingen.de/de/forschung/zellbiologie-neurologischer-erkrankungen/forschungsgruppen-und-units/unit-demenzforschung/",
        "https://www.hih-tuebingen.de/de/presse/pressemitteilungen/artikel/15-eva-luise-koehler-forschungspreis-auszeichnung-einer-therapieentwicklung-fuer-die-neurologische-e/",
        "https://www.hih-tuebingen.de/de/presse/pressemitteilungen/artikel/das-hertie-institut-fuer-klinische-hirnforschung-feiert-sein-20-jaehriges-bestehen/",
        "https://www.hih-tuebingen.de/de/presse/pressemitteilungen/artikel/das-hertie-institut-fuer-klinische-hirnforschung-feiert-sein-20-jaehriges-bestehen/ /",
        "https://www.hih-tuebingen.de/en/",
        "https://www.hih-tuebingen.de/en/career/career-opportunities/current-career-opportunities/",
        "https://www.hih-tuebingen.de/en/career/career-opportunities/students/",
        "https://www.hih-tuebingen.de/en/career/support-programmes-for-women/",
        "https://www.hih-tuebingen.de/en/career/tuewin-group/",
        "https://www.hih-tuebingen.de/en/career/work-and-family-life/",
        "https://www.hih-tuebingen.de/en/forschung/independent-research-groups/junior-research-group-randolph-helfrich/",
        "https://www.hih-tuebingen.de/en/research/",
        "https://www.hih-tuebingen.de/en/research/cellular-neurology/",
        "https://www.hih-tuebingen.de/en/research/cellular-neurology/research-groups-and-units/dementia-research-unit/",
        "https://www.hih-tuebingen.de/en/research/cellular-neurology/research-groups-and-units/experimental-neuroimmunology/",
        "https://www.hih-tuebingen.de/en/research/cellular-neurology/research-groups-and-units/experimental-neuropathology/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/cognitive-neurology/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/human-intracranial-cognitive-neurophysiology/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/mocom/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/molecular-brain-development/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/neuron-glia-interactions/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/neuropsychology-of-action/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/oculomotor-laboratory/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/section-for-computational-sensomotorics/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/section-for-neuropsychology/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/section-for-translational-genomics-of-neurodegenerative-diseases/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/systems-neurophysiology-lab/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/translational-genomics/ekfs-forschungskolleg-precisenet/",
        "https://www.hih-tuebingen.de/en/research/independent-research-groups/translational-imaging-of-cortical-microstructure/",
        "https://www.hih-tuebingen.de/en/research/neural-dynamics/neural-dynamics-and-magnetoencephalography/",
        "https://www.hih-tuebingen.de/en/research/neuro-oncology/",
        "https://www.hih-tuebingen.de/en/research/neuro-oncology/about-us/",
        "https://www.hih-tuebingen.de/en/research/neuro-oncology/ekfs-forschungskolleg-therapieresistenz-solider-tumore/",
        "https://www.hih-tuebingen.de/en/research/neuro-oncology/research-groups/experimental-pediatric-neuro-oncology/",
        "https://www.hih-tuebingen.de/en/research/neuro-oncology/research-groups/health-care-research-in-neuro-oncology/",
        "https://www.hih-tuebingen.de/en/research/neuro-oncology/research-groups/laboratory-for-clinical-and-experimental-neuro-oncology/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/clinical-parkinson-research/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/deep-brain-stimulation/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/dystonia/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/functional-neurogenetics/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/genetics-of-parkinsons-disease/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/genomic-of-rare-movement-disorders/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/mitochondrial-biology-of-parkinsons-disease/",
        "https://www.hih-tuebingen.de/en/research/neurodegenerative-diseases/research-groups/section-for-clinical-neurogenetics/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-epileptology/research-groups/experimental-epileptology/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-epileptology/research-groups/experimental-neurophysiology-of-channelopathies/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-epileptology/research-groups/molecular-and-translational-neurosurgical-epileptology/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-epileptology/research-groups/neuromuscular-imaging-group/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-stroke/research-groups-and-foci/brain-networks-and-plasticity/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-stroke/research-groups-and-foci/molecular-neurooncology/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-stroke/research-groups-and-foci/neurological-b-cell-immunology-group/",
        "https://www.hih-tuebingen.de/en/research/neurology-and-stroke/research-groups-and-foci/stroke-and-neuroprotection/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/dystonie/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/funktionelle-neurogenetik/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/genomik-seltener-bewegungsstoerungen/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/klinische-parkinsonforschung/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/mitochondriale-biologie-der-parkinson-krankheit/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/parkinson-genetik/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/sektion-klinische-neurogenetik/",
        "https://www.hih-tuebingen.de/forschung/neurodegeneration/forschungsgruppen/tiefe-hirnstimulation/",
        "https://www.hih-tuebingen.de/forschung/neurologie-mit-schwerpunkt-epileptologie/forschungsgruppen/experimentelle-epileptologie/",
        "https://www.hih-tuebingen.de/forschung/neurologie-mit-schwerpunkt-epileptologie/forschungsgruppen/experimentelle-neurophysiologie-von-kanalerkrankungen/",
        "https://www.hih-tuebingen.de/forschung/neurologie-mit-schwerpunkt-epileptologie/forschungsgruppen/molekulare-und-translationale-neurochirurgische-epileptologie/",
        "https://www.hih-tuebingen.de/forschung/neurologie-mit-schwerpunkt-epileptologie/forschungsgruppen/neuromuskulaere-bildgebung/",
        "https://www.hih-tuebingen.de/forschung/neuronale-dynamik/neuronale-dynamik-und-magnetenzephalographie/",
        "https://www.hih-tuebingen.de/forschung/neuroonkologie/",
        "https://www.hih-tuebingen.de/forschung/neuroonkologie/forschungsgruppen/experimentelle-paediatrische-neuroonkologie/",
        "https://www.hih-tuebingen.de/forschung/neuroonkologie/forschungsgruppen/labor-fuer-klinische-und-experimentelle-neuroonkologie/",
        "https://www.hih-tuebingen.de/forschung/neuroonkologie/forschungsgruppen/neuroonkologische-versorgungsforschung/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/intrakranielle-kognitive-neurophysiologie/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/kognitive-neurologie/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/labor-fuer-aktive-wahrnehmung/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/labor-fuer-systemische-neurophysiologie/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/mocom/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/molekulare-hirnentwicklung/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/neuron-glia-interaktionen/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/neuropsychologie-der-handlungskontrolle/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/okulomotorik-labor/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/sektion-neuropsychologie/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/sektion-theoretische-sensomotorik/",
        "https://www.hih-tuebingen.de/forschung/unabhaengige-forschungsgruppen/sektion-translationale-genomik-neurodegenerativer-erkrankungen/",
        "https://www.hih-tuebingen.de/forschung/vaskulaere-neurologie/forschungsgruppen/molekulare-neuroonkologie/",
        "https://www.hih-tuebingen.de/forschung/vaskulaere-neurologie/forschungsgruppen/neurologische-b-zell-immunologie/",
        "https://www.hih-tuebingen.de/forschung/vaskulaere-neurologie/forschungsgruppen/neuroplastizitaet/",
        "https://www.hih-tuebingen.de/forschung/vaskulaere-neurologie/forschungsgruppen/stroke-and-neuroprotection/",
        "https://www.hih-tuebingen.de/forschung/zellbiologie-neurologischer-erkrankungen/forschungsgruppen-und-units/experimentelle-neuro-immunologie/",
        "https://www.hih-tuebingen.de/forschung/zellbiologie-neurologischer-erkrankungen/forschungsgruppen-und-units/experimentelle-neuropathologie/",
        "https://www.hih-tuebingen.de/",
        "https://www.hih-tuebingen.de/presse/pressemitteilungen/artikel/ich-sehe-was-das-du-gleich-sagen-wirst/",
        "https://www.hofgutrosenau-tuebingen.de/",
        "https://www.holzland-tuebingen.de/",
        "https://www.hospiz-tuebingen.de/",
        "https://www.hospiz-tuebingen.de/begleitung/",
        "https://www.hospiz-tuebingen.de/datenschutzhinweise/",
        "https://www.hospiz-tuebingen.de/hospiz-tuebingen/",
        "https://www.hospiz-tuebingen.de/impressionen/",
        "https://www.hospiz-tuebingen.de/impressum/",
        "https://www.hospiz-tuebingen.de/kontakt/",
        "https://www.hospiz-tuebingen.de/merrit-peter-renz-haus/",
        "https://www.hospiz-tuebingen.de/spenden/",
        "https://www.hsp.uni-tuebingen.de/",
        "https://www.hsp.uni-tuebingen.de/kraft/index.html",
        "https://www.humangenetik-tuebingen.de/",
        "https://www.humangenetik-tuebingen.de/seltene-erkrankungen/epilepsie-und-hirnentwicklungsstoerungen/",
        "https://www.hwk-reutlingen.de/weiterbildung/bildungsakademien/tuebingen.html",
        "https://www.icfa-tuebingen.de/",
        "https://www.ifs.uni-tuebingen.de/institut.html",
        "https://www.immunology-tuebingen.de/",
        "https://www.infoe-tuebingen.de/",
        "https://www.infosperber.ch/politik/europa/einwegsteuer-tuebingen-legt-sich-mit-mcdonalds-an/",
        "https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/#comment-166663/",
        "https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/#comment-166703/",
        "https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/#comment-166709/",
        "https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/#comment-166721/",
        "https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/#comment-166749/",
        "https://www.instagram.com/biwakschachtel_tuebingen/",
        "https://www.instagram.com/chocolat.tuebingen/",
        "https://www.instagram.com/christian.kuehn.tuebingen/",
        "https://www.instagram.com/contigofairtradetuebingen/",
        "https://www.instagram.com/cvjmtuebingen/",
        "https://www.instagram.com/daituebingen.library/",
        "https://www.instagram.com/daituebingen/",
        "https://www.instagram.com/davtuebingen/",
        "https://www.instagram.com/drk_kv_tuebingen/",
        "https://www.instagram.com/elsa_tuebingen/",
        "https://www.instagram.com/esg_tuebingen/",
        "https://www.instagram.com/feuerwehr.tuebingen/",
        "https://www.instagram.com/fridaysforfuture_tuebingen/",
        "https://www.instagram.com/galeriegriesshaber_tuebingen/",
        "https://www.instagram.com/geburtshaus.tuebingen/",
        "https://www.instagram.com/gehrtuebingen/",
        "https://www.instagram.com/genussart_tuebingen/",
        "https://www.instagram.com/gruenetuebingen/",
        "https://www.instagram.com/hkm_tuebingen/",
        "https://www.instagram.com/hotelamschloss_tuebingen/",
        "https://www.instagram.com/jgr_tuebingen/",
        "https://www.instagram.com/juwelier_seeger_tuebingen/",
        "https://www.instagram.com/kathrinschustertuebingen/",
        "https://www.instagram.com/khgtuebingen/",
        "https://www.instagram.com/kreisbau.tuebingen/",
        "https://www.instagram.com/kunsthalletuebingen/",
        "https://www.instagram.com/lebenshilfe.tuebingen/",
        "https://www.instagram.com/meypostsvtubingen/",
        "https://www.instagram.com/morejoe_tuebingen/",
        "https://www.instagram.com/nikolauslauf_tuebingen/",
        "https://www.instagram.com/olivle_tuebingen_/",
        "https://www.instagram.com/pfadfinder_tuebingen/",
        "https://www.instagram.com/roundnet_tuebingen/",
        "https://www.instagram.com/s_haeaes_tuebingen/",
        "https://www.instagram.com/stadttuebingen/",
        "https://www.instagram.com/stadtwerketuebingen/",
        "https://www.instagram.com/sv03_tuebingen/",
        "https://www.instagram.com/thwtuebingen/",
        "https://www.instagram.com/tigers_tuebingen/",
        "https://www.instagram.com/toastmasters_tuebingen/",
        "https://www.instagram.com/trigirls_tuebingen/",
        "https://www.instagram.com/tsg_tuebingen/",
        "https://www.instagram.com/ttcrotgoldtuebingen/",
        "https://www.instagram.com/tuebingen.kohenoor/",
        "https://www.instagram.com/ubtuebingen/",
        "https://www.instagram.com/uniklinikum.tuebingen/",
        "https://www.instagram.com/universitaet.tuebingen/",
        "https://www.instagram.com/unsertuebingen/",
        "https://www.instagram.com/vegi_tuebingen/",
        "https://www.instagram.com/vhstuebingen/",
        "https://www.instagram.com/visittuebingen/",
        "https://www.instagram.com/yoga_loft_tuebingen/",
        "https://www.institutfrancais.de/tubingen/",
        "https://www.intersport-raepple.de/filialen/raepple-tuebingen/",
        "https://www.intersport.de/haendlersuche/sportgeschaefte-baden-wuerttemberg/72072-tuebingen-intersport-raepple-1/",
        "https://www.is.tuebingen.mpg.de/nc/employee/details/mschober.html",
        "https://www.is.tuebingen.mpg.de/nc/employee/details/phennig.html",
        "https://www.isct.uni-tuebingen.de/wsic/",
        "https://www.iwm-tuebingen.de/www/de/forschung/forschungsbereiche/index.html#wct2009/",
        "https://www.iwm-tuebingen.de/www/de/index.html",
        "https://www.iwm-tuebingen.de/www/en/index.html",
        "https://www.iwm-tuebingen.de/www/en/karriere/stellenangebote/index.html",
        "https://www.iwm-tuebingen.de/www/en/stellenangebote/index.html",
        "https://www.iwm-tuebingen.de/www/index.html",
        "https://www.jacques.de/depot/44/tuebingen/",
        "https://www.jacques.de/depot/44/tuebingen/email-schreiben/",
        "https://www.jazzclub-tuebingen.de/",
        "https://www.jgr-tuebingen.de/",
        "https://www.jobcenter-tuebingen.de/digital/",
        "https://www.jobcenter-tuebingen.de/kontakte/",
        "https://www.johanniter.de/dienstleistungen/pflege-und-beratung/pflegedienste/ambulante-pflegedienste/ambulante-pflege-in-tuebingen/",
        "https://www.jugendagentur-tuebingen.de/",
        "https://www.jugendherberge-tuebingen.de/",
        "https://www.jugendherberge.de/en/youth-hostels/tuebingen-113/prices/",
        "https://www.jugendkirche-tuebingen.de/",
        "https://www.juki-tuebingen.de/",
        "https://www.jura.uni-tuebingen.de/einrichtungen/ifk/",
        "https://www.jura.uni-tuebingen.de/index.html",
        "https://www.karg-und-petersen.de/en/portfolio-item/eberhard-karls-universitaet-tuebingen-image-brochure/",
        "https://www.karg-und-petersen.de/portfolio-item/eberhard-karls-universitaet-tuebingen-imagebroschuere/",
        "https://www.karg-und-petersen.de/portfolio-item/universitaetsstadt-tuebingen-sozialbericht-flyer-roll-ups-und-banner/",
        "https://www.karg-und-petersen.de/portfolio-item/volksbank-tuebingen-jubilaeumskampagne-geschaeftsbericht/",
        "https://www.kath-theol.uni-tuebingen.de/",
        "https://www.keb-tuebingen.de/",
        "https://www.keb-tuebingen.de/agb/",
        "https://www.keb-tuebingen.de/aktuelles/",
        "https://www.keb-tuebingen.de/datenschutz/",
        "https://www.keb-tuebingen.de/impressum/",
        "https://www.keb-tuebingen.de/info/",
        "https://www.keb-tuebingen.de/info/unsere-geschaefsstelle/",
        "https://www.keb-tuebingen.de/info/unsere-kooperationen/",
        "https://www.keb-tuebingen.de/info/unsere-referentinnen/",
        "https://www.keb-tuebingen.de/kalender/",
        "https://www.keb-tuebingen.de/kontakt/",
        "https://www.keb-tuebingen.de/kw/blkeep/1/month/6/year/2023/kfs_veranartids/-1#kalender/",
        "https://www.keb-tuebingen.de/kw/blkeep/1/month/8/year/2023/kfs_veranartids/-1#kalender/",
        "https://www.keb-tuebingen.de/newsletter/",
        "https://www.keb-tuebingen.de/programm/",
        "https://www.keb-tuebingen.de/programm/achtsamkeit-und-begegnung/",
        "https://www.keb-tuebingen.de/programm/achtsamkeit-und-begegnung/kw/bereich/kursdetails/kurs/230116-2/kursname/Einfuehrung_ins_kontemplative_Gebet/kategorie-id/8/",
        "https://www.keb-tuebingen.de/programm/achtsamkeit-und-begegnung/kw/bereich/kursdetails/kurs/230205/kursname/Tanzen_-_den_Augenblick_leben/kategorie-id/8/",
        "https://www.keb-tuebingen.de/programm/achtsamkeit-und-begegnung/kw/bereich/kursdetails/kurs/230729/kursname/Pilgern_auf_dem_Martinusweg_mit_Bischof_Gebhard_Fuerst/kategorie-id/8/",
        "https://www.keb-tuebingen.de/programm/achtsamkeit-und-begegnung/kw/bereich/kursdetails/kurs/231006-1/kursname/Fuehrung im Garten von Professor Doschka/kategorie-id/8/",
        "https://www.keb-tuebingen.de/programm/familie-und-erziehung/",
        "https://www.keb-tuebingen.de/programm/familie-und-erziehung/kw/bereich/kursdetails/kurs/230419/kursname/Offener_Elterntreff_in_Rottenburg_am_Mittwoch/kategorie-id/14/",
        "https://www.keb-tuebingen.de/programm/familie-und-erziehung/kw/bereich/kursdetails/kurs/230420/kursname/Offener_Elterntreff_in_Rottenburg_am_Donnerstag_KiGa_St_Remigius/kategorie-id/14/",
        "https://www.keb-tuebingen.de/programm/familie-und-erziehung/kw/bereich/kursdetails/kurs/230421/kursname/Offener_Elterntreff_in_Rottenburg_am_Freitag/kategorie-id/14/",
        "https://www.keb-tuebingen.de/programm/familie-und-erziehung/kw/bereich/kursdetails/kurs/231002/kursname/ROBBY - Maxis fuer Kinder geboren zwischen September 22 und Dezember 22/kategorie-id/14/",
        "https://www.keb-tuebingen.de/programm/familie-und-erziehung/kw/bereich/kursdetails/kurs/231116/kursname/Praeventionsschulung A1 gegen sexualisierte Gewalt/kategorie-id/14/",
        "https://www.keb-tuebingen.de/programm/glaube-und-gesellschaft/",
        "https://www.keb-tuebingen.de/programm/glaube-und-gesellschaft/kw/bereich/kursdetails/kurs/240122/kursname/Wie bekommt die Dioezese Rottenburg-Stuttgart einen neuen Bischof/kategorie-id/5/",
        "https://www.keb-tuebingen.de/programm/kreuz-und-quer/",
        "https://www.keb-tuebingen.de/programm/kw/kathaupt/621/datum/07.07.2023/k0/230421/k1/230113-2/",
        "https://www.keb-tuebingen.de/programm/kw/kathaupt/621/datum/16.07.2023/k0/230507/k1/230423/",
        "https://www.keb-tuebingen.de/programm/kw/kathaupt/621/datum/21.07.2023/k0/230421/k1/230721-2/k2/230721-1/",
        "https://www.keb-tuebingen.de/programm/kw/kathaupt/621/datum/26.07.2023/k0/230419/k1/230329/",
        "https://www.keb-tuebingen.de/programmheft/",
        "https://www.keb-tuebingen.de/suche/",
        "https://www.keb-tuebingen.de/teilnehmer-login/kw/kathaupt/266/",
        "https://www.keb-tuebingen.de/unser-verein/",
        "https://www.keb-tuebingen.de/warenkorb/kw/bereich/warenkorb/",
        "https://www.keb-tuebingen.de/widerruf/",
        "https://www.kfv-tuebingen.de/",
        "https://www.khg-chor-tuebingen.de/",
        "https://www.khg-tuebingen.de/",
        "https://www.khs-tuebingen.de/",
        "https://www.kidojotuebingen.de/",
        "https://www.kieser-training.de/studios/tuebingen/",
        "https://www.kijufa-tuebingen.de/",
        "https://www.kinderhaus-tuebingen.de/",
        "https://www.kinderschutzbund-tuebingen.de/",
        "https://www.kirchenbezirk-tuebingen.de/",
        "https://www.kirchenbezirk-tuebingen.de/bezirk/diakonisches-werk/",
        "https://www.kirchenbezirk-tuebingen.de/service/veranstaltungen/",
        "https://www.kirnbachschule-tuebingen.de/",
        "https://www.kita-kreuzkirche-tuebingen.de/",
        "https://www.kita-tuebingen.de/",
        "https://www.klinikschule-tuebingen.de/",
        "https://www.klinikseelsorge-tuebingen.de/",
        "https://www.klinikseelsorge-tuebingen.de/index.php/team.html",
        "https://www.kokon-tuebingen.de/",
        "https://www.kompass-tuebingen.de/",
        "https://www.konzerte-tuebingen.de/",
        "https://www.konzerte-tuebingen.de/konzerte/",
        "https://www.konzerte-tuebingen.de/konzerte/sommerkonzerte-2019/",
        "https://www.kov-tuebingen.de/mitgliedsvereine-neu/222-obst-gartenbauverein-weilheim-e-v.html",
        "https://www.kreis-tuebingen.de/",
        "https://www.kreis-tuebingen.de/,(anker1243549)/307823.html#anker1243549/",
        "https://www.kreis-tuebingen.de/,(anker1243549)/Startseite/landratsamt/abteilung+31+-+umwelt+und+gewerbe.html#anker1243549/",
        "https://www.kreis-tuebingen.de/,Lde/11398752.html",
        "https://www.kreis-tuebingen.de/,Lde/11414095.html",
        "https://www.kreis-tuebingen.de/,Lde/307325.html",
        "https://www.kreis-tuebingen.de/,Lde/308135.html",
        "https://www.kreis-tuebingen.de/,Lde/308593.html",
        "https://www.kreis-tuebingen.de/,Lde/309023.html",
        "https://www.kreis-tuebingen.de/,Lde/309062.html",
        "https://www.kreis-tuebingen.de/,Lde/309170.html",
        "https://www.kreis-tuebingen.de/,Lde/315475.html",
        "https://www.kreis-tuebingen.de/,Lde/Beratungsstelle+fuer+Menschen+mit+Behinderungen+und+ihre+Familien.html",
        "https://www.kreis-tuebingen.de/,Lde/Erforderliche+Unterlagen+zur+Kfz-Zulassung.html",
        "https://www.kreis-tuebingen.de/,Lde/Kfz-Zulassungsstelle.html",
        "https://www.kreis-tuebingen.de/,Lde/Sorgeerklaerungen+und+_register.html",
        "https://www.kreis-tuebingen.de/,Lde/Startseite/sichere+Kommunikation.html",
        "https://www.kreis-tuebingen.de/,Ldnaldo%20ticket%20shope/309062.html",
        "https://www.kreis-tuebingen.de/13390825.html",
        "https://www.kreis-tuebingen.de/13451032.html",
        "https://www.kreis-tuebingen.de/17337781.html",
        "https://www.kreis-tuebingen.de/307274.html",
        "https://www.kreis-tuebingen.de/belehrung/",
        "https://www.kreis-tuebingen.de/but/",
        "https://www.kreis-tuebingen.de/energieschulden/",
        "https://www.kreis-tuebingen.de/Fahrerlaubnisse/",
        "https://www.kreis-tuebingen.de/kuehlschrankpraemie/",
        "https://www.kreis-tuebingen.de/onlinedienste/",
        "https://www.kreis-tuebingen.de/Startseite.html",
        "https://www.kreis-tuebingen.de/Startseite/landratsamt/ehrenamt+gemeinsam+aktiv.html",
        "https://www.kreis-tuebingen.de/Startseite/landratsamt/Gemeinsam+aktiv+fuer+Fluechtlinge_.html",
        "https://www.kreis-tuebingen.de/Startseite/landratsamt/grundsicherung+im+alter+und+bei+erwerbsminderung+_sgb+xii_.html",
        "https://www.kreisseniorenrat-tuebingen.de/",
        "https://www.kreuzkirche-tuebingen.de/",
        "https://www.krone-tuebingen.de/",
        "https://www.ksk-tuebingen.de/",
        "https://www.ksk-tuebingen.de/de/home.html",
        "https://www.ksk-tuebingen.de/de/home/service/filiale-finden.html",
        "https://www.kuenstlerbund-tuebingen.de/",
        "https://www.kulturnacht-tuebingen.de/",
        "https://www.kulturnetz-tuebingen.de/",
        "https://www.kulturnetz-tuebingen.de/artuethek/",
        "https://www.kulturnetz-tuebingen.de/artuethek/freischaltung-beantragen/",
        "https://www.kulturnetz-tuebingen.de/datenschutzerklaerung/",
        "https://www.kulturnetz-tuebingen.de/events/",
        "https://www.kulturnetz-tuebingen.de/faq/",
        "https://www.kulturnetz-tuebingen.de/impressum/",
        "https://www.kulturnetz-tuebingen.de/informationen/",
        "https://www.kulturnetz-tuebingen.de/institutionen/",
        "https://www.kulturnetz-tuebingen.de/kulturszene/",
        "https://www.kulturnetz-tuebingen.de/kunstprofil/",
        "https://www.kulturnetz-tuebingen.de/kunstprofilekategorien/kunstrichtungen/bildende-kunst/",
        "https://www.kulturnetz-tuebingen.de/kunstprofilekategorien/kunstrichtungen/musik/",
        "https://www.kulturnetz-tuebingen.de/kunstwerke/",
        "https://www.kulturnetz-tuebingen.de/runder-tisch-kultur-12-juli-2023/",
        "https://www.kulturnetz-tuebingen.de/runder-tisch-kultur-18-april-2023-2/",
        "https://www.kulturnetz-tuebingen.de/runder-tisch-kultur-5-april-2022/",
        "https://www.kulturnetz-tuebingen.de/runder-tisch-kultur/",
        "https://www.kulturnetz-tuebingen.de/service/",
        "https://www.kulturnetz-tuebingen.de/service/login/",
        "https://www.kulturnetz-tuebingen.de/service/registration/",
        "https://www.kulturnetz-tuebingen.de/ueber-uns/",
        "https://www.kulturnetz-tuebingen.de/veranstaltungen/",
        "https://www.kulturnetz-tuebingen.de/veranstaltungen/jazz-und-klassiktage/",
        "https://www.kulturnetz-tuebingen.de/veranstaltungen/kulturnacht/",
        "https://www.kunsthalle-tuebingen.de/",
        "https://www.kununu.com/de/stadtwerke-tuebingen/",
        "https://www.kupferblau.de/2020/12/18/die-besten-take-away-geheimtipps-in-tuebingen/",
        "https://www.kupferblau.de/2020/12/18/die-besten-take-away-geheimtipps-in-tuebingen/#respond/",
        "https://www.kupferblau.de/2023/07/14/wie-viel-geld-ist-fuer-universitaeten-uebrig-finanzminister-bayaz-in-tuebingen/",
        "https://www.kupferblau.de/tag/tubingen/",
        "https://www.kupferblau.de/tag/uni-tuebingen/",
        "https://www.kurende-tuebingen.de/",
        "https://www.kyb.tuebingen.mpg.de/",
        "https://www.kyb.tuebingen.mpg.de/career/working-at-the-mpi.html",
        "https://www.kyb.tuebingen.mpg.de/computational-neuroscience/",
        "https://www.kyb.tuebingen.mpg.de/en/",
        "https://www.kyb.tuebingen.mpg.de/imprs-mmfd/",
        "https://www.kyb.tuebingen.mpg.de/person/103915/2537/",
        "https://www.la-cantinella-tuebingen.de/",
        "https://www.lacasa-tuebingen.de/",
        "https://www.lamm-tuebingen.de/",
        "https://www.landestheater-tuebingen.de/",
        "https://www.landestheater-tuebingen.de/downloads/78625_Pressefotos_Sophie_Scholl.zip/",
        "https://www.landestheater-tuebingen.de/downloads/79745_Pressefotos_Ein_groser_Aufbruch.zip/",
        "https://www.landestheater-tuebingen.de/downloads/79920_Pressefotos_Der_Prozess.zip/",
        "https://www.landestheater-tuebingen.de/downloads/80350_Pressefotos_Meine_Eltern.zip/",
        "https://www.landestheater-tuebingen.de/downloads/80430_Pressefotos_Shopping_Animals.zip/",
        "https://www.landestheater-tuebingen.de/downloads/80680_Pressefotos_PERPLEX.zip/",
        "https://www.landestheater-tuebingen.de/downloads/81185_Pressefotos_Tagebuch_eines_Wahnsinnigen.zip/",
        "https://www.landestheater-tuebingen.de/downloads/81268_Pressefotos_MONSTA.zip/",
        "https://www.landestheater-tuebingen.de/downloads/81449_Pressefotos_Die_kahle_Saengerin.zip/",
        "https://www.landestheater-tuebingen.de/downloads/81566_Pressefotos_Ach_Mensch.zip/",
        "https://www.landestheater-tuebingen.de/downloads/81569_Pressefotos_Maria_Stuart.zip/",
        "https://www.landestheater-tuebingen.de/downloads/81669_Pressefotos_Wir_rennen_ins_Offene_LTT_Labor.zip/",
        "https://www.landestheater-tuebingen.de/downloads/81897_Pressefotos_Liebesbriefe_an_Hitler.zip/",
        "https://www.landestheater-tuebingen.de/downloads/82956_Pressefotos_LTT_DIE_STADT_DER_BLINDEN.zip/",
        "https://www.landestheater-tuebingen.de/downloads/82986_Pressefotos_REvolution.zip/",
        "https://www.landestheater-tuebingen.de/downloads/83988_Pressefotos_BUNBURY.zip/",
        "https://www.landestheater-tuebingen.de/downloads/83993_Pressefotos_Der_gute_Gott_von_Manhattan.zip/",
        "https://www.landestheater-tuebingen.de/downloads/84137_Pressefotos_Siri_und_die_Eismeerpiraten.zip/",
        "https://www.landestheater-tuebingen.de/downloads/84669_Pressefotos_Frauentheater_Muetter.zip/",
        "https://www.landestheater-tuebingen.de/downloads/84742_PRESSEFOTOS_HABEN_WOLLEN_PROJEKTWERKSTATT.zip/",
        "https://www.landestheater-tuebingen.de/downloads/84911_Pressefotos_Magical_Mystery.zip/",
        "https://www.landestheater-tuebingen.de/downloads/84998_Pressefotos_Quartett.zip/",
        "https://www.landestheater-tuebingen.de/downloads/85078_Pressefotos_Woyzeck.zip/",
        "https://www.landestheater-tuebingen.de/downloads/85196_Pressefotos_Im_Thurm.zip/",
        "https://www.landestheater-tuebingen.de/downloads/85305_Pressefotos_Angstmaen.zip/",
        "https://www.landestheater-tuebingen.de/downloads/85824_Pressefotos_Der_Fiskus.zip/",
        "https://www.landestheater-tuebingen.de/downloads/85826_Pressefotos_Jenseits_von_Eden.zip/",
        "https://www.landestheater-tuebingen.de/downloads/86186_Pressefotos_Theatersport.zip/",
        "https://www.landestheater-tuebingen.de/downloads/86886_Pressefotos_Landing_on_an_unknown_Planet.zip/",
        "https://www.landestheater-tuebingen.de/downloads/86996_Pressefotos_Ich_waer_gern_voller_Zuversicht_LTT_Labor.zip/",
        "https://www.landestheater-tuebingen.de/downloads/87056_Pressefotos_Fuenf_vor_High_Noon.zip/",
        "https://www.landestheater-tuebingen.de/downloads/88430_Pressefotos_Oekozid.zip/",
        "https://www.landestheater-tuebingen.de/downloads/88450_Pressefotos_Orlando.zip/",
        "https://www.landestheater-tuebingen.de/downloads/89011_Pressefotos_Die_Drei_Raeuber.zip/",
        "https://www.landestheater-tuebingen.de/downloads/89214_Pressefotos_Sex.zip/",
        "https://www.landestheater-tuebingen.de/downloads/89319_Pressefotos_Vom_Wert_des_Leberkaesweckles.zip/",
        "https://www.landestheater-tuebingen.de/downloads/89658_Pressefotos_Marylin.zip/",
        "https://www.landestheater-tuebingen.de/downloads/89790_Pressefotos_Halt_Generationentheater_Zeitsprung.zip/",
        "https://www.landestheater-tuebingen.de/downloads/90219_Pressefotos_Der_erste_fiese_Typ.zip/",
        "https://www.landestheater-tuebingen.de/downloads/90220_Pressefotos_Arturo_Ui.zip/",
        "https://www.landestheater-tuebingen.de/downloads/90287_Pressefotos_Great_Balls_of_Fire.zip/",
        "https://www.landestheater-tuebingen.de/downloads/90513_Pressefotos_Wolkenrotz.zip/",
        "https://www.landestheater-tuebingen.de/downloads/90923_Pressefotos_Hitlers_Ziege_und_die_Haemorrhoiden_des_Koenigs.zip/",
        "https://www.landestheater-tuebingen.de/downloads/91222_Pressefotos_Orest.zip/",
        "https://www.landestheater-tuebingen.de/downloads/91228_Pressefotos_Gullivers_Reisen.zip/",
        "https://www.landestheater-tuebingen.de/downloads/91770_Pressefotos_wyld_and_classy.zip/",
        "https://www.landestheater-tuebingen.de/downloads/91855_Pressefotos_Tittipics.zip/",
        "https://www.landestheater-tuebingen.de/downloads/91948_Pressefotos_Endstation_Sehnsucht_LTT.zip/",
        "https://www.landestheater-tuebingen.de/downloads/91954_Presse_KUNST.zip/",
        "https://www.landestheater-tuebingen.de/spielplan/-bdquo-kunst-ldquo--6237/",
        "https://www.landestheater-tuebingen.de/spielplan/angstm-n-6026/",
        "https://www.landestheater-tuebingen.de/spielplan/der-ursprung-der-liebe-5820/",
        "https://www.landestheater-tuebingen.de/spielplan/die-drei-r-auml-uber-6075/",
        "https://www.landestheater-tuebingen.de/spielplan/endstation-sehnsucht-6072/",
        "https://www.landestheater-tuebingen.de/spielplan/great-balls-of-fire--6227/",
        "https://www.landestheater-tuebingen.de/spielplan/gullivers-reisen-6071/",
        "https://www.landestheater-tuebingen.de/spielplan/harder--faster--stronger-5812/",
        "https://www.landestheater-tuebingen.de/spielplan/hitlers-ziege-und-die-h-auml-morrhoiden-des-k-ouml-nigs-6070/",
        "https://www.landestheater-tuebingen.de/spielplan/ich-w-auml-r-rsquo--gern-voller-zuversicht-6140/content/",
        "https://www.landestheater-tuebingen.de/spielplan/judas-5811/",
        "https://www.landestheater-tuebingen.de/spielplan/klamms-krieg-5763/",
        "https://www.landestheater-tuebingen.de/spielplan/landing-on-an-unknown-planet-6190/",
        "https://www.landestheater-tuebingen.de/spielplan/m-tter-6114/",
        "https://www.landestheater-tuebingen.de/spielplan/magical-mystery-6119/",
        "https://www.landestheater-tuebingen.de/spielplan/monsta-5896/",
        "https://www.landestheater-tuebingen.de/spielplan/orest-6073/",
        "https://www.landestheater-tuebingen.de/spielplan/peter-und-der-wolf-5758/",
        "https://www.landestheater-tuebingen.de/spielplan/sandmann--lieber-sandmann-5485/",
        "https://www.landestheater-tuebingen.de/spielplan/shopping-animals-5898/",
        "https://www.landestheater-tuebingen.de/spielplan/sophie-scholl%253A-allen-gewalten-zum-trotz-sich-erhalten-5971/",
        "https://www.landestheater-tuebingen.de/Spielplan/Theaterpaedagogik/Schultheatertage.html",
        "https://www.landestheater-tuebingen.de/Spielplan/Theaterpaedagogik/Theater_fuer_Alle.html",
        "https://www.landestheater-tuebingen.de/spielplan/vom-wert-des-leberk-auml-sweckles-6067/",
        "https://www.landestheater-tuebingen.de/spielplan/wahlbekanntschaften-5814/",
        "https://www.landestheater-tuebingen.de/spielplan/woyzeck-6021/",
        "https://www.landestheater-tuebingen.de/Theaterpaedagogik/Theater_fuer_Alle.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/90005/Folge_4_des_LTT_Podcast%3A_Die_Verwandlung.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/90853/Krankheitsbedingter_Vorstellungsausfall_am_27-_Mai_-_-Ouml-kozid.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/91670/Zahlt_doch-_was_ihr_wollt-.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/91722/Tennessee_Williams_und_Yasmina_Reza.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/91860/Backstagef-uuml-hrung_durch_das_LTT.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/91965/Programmheft_-quot-Endstation_Sehnsucht-quot-.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/92030/-quot-Kunst-quot-_-middot-_Heute_geht-s_in_den_Saal-.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/92065/Geld_oder_was_im_Leben_sonst_so_fehlt_-_Ein_Abend_des_LTT-Labor.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/92179/Die_neue_Spielzeit_23_24_am_LTT.html",
        "https://www.landestheater-tuebingen.de/weblog/neu_wichtig/view/dt/3/article/92232/Endspurt_am_LTT.html",
        "https://www.landgericht-tuebingen.de/",
        "https://www.landkreis-tuebingen.de/",
        "https://www.lav-tuebingen.de/",
        "https://www.lbs.de/beratung/sw/tuebingen_9/tuebingen_11/andreas_sailer_1/index_12819235.jsp/",
        "https://www.lebenshilfe-tuebingen.de/",
        "https://www.lebenshilfe-tuebingen.de/angebote/aelter-werden/",
        "https://www.lebenshilfe-tuebingen.de/angebote/arbeitsgemeinschaft-staedtepartnerschaft/",
        "https://www.lebenshilfe-tuebingen.de/angebote/einzelassistenz/",
        "https://www.lebenshilfe-tuebingen.de/angebote/familien-mit-migrationshintergund/",
        "https://www.lebenshilfe-tuebingen.de/angebote/frauen-treffen-frauen/",
        "https://www.lebenshilfe-tuebingen.de/angebote/kunst-und-kultur/kunst-kaufen/",
        "https://www.lebenshilfe-tuebingen.de/angebote/vereinsbegleitung/",
        "https://www.lebenshilfe-tuebingen.de/mitmachen/",
        "https://www.lebenshilfe-tuebingen.de/mitmachen/mitglied-werden/",
        "https://www.lebenshilfe-tuebingen.de/service/kosten-anmelde-und-ruecktrittsregelungen/",
        "https://www.lebenshilfe-tuebingen.de/service/termine/",
        "https://www.lebenshilfe-tuebingen.de/top-oben/datenschutz/",
        "https://www.lebenshilfe-tuebingen.de/top-oben/singleview/die-neue-app-der-lebenshilfe-tuebingen/",
        "https://www.lebenshilfe-tuebingen.de/top-oben/singleview/sommerprogramm/",
        "https://www.lebenshilfe-tuebingen.de/top-oben/start/#&panel1-1/",
        "https://www.lebenshilfe-tuebingen.de/ueber-uns/leitbild/",
        "https://www.lebenshilfe-tuebingen.de/ueber-uns/organigramm/",
        "https://www.lebenshilfe-tuebingen.de/ueber-uns/satzung/",
        "https://www.lebenshilfe-tuebingen.de/ueber-uns/vorstand/",
        "https://www.leibniz-kolleg.uni-tuebingen.de/",
        "https://www.linkedin.com/company/rak-tuebingen/",
        "https://www.lpb-bw.de/ob-wahl-tuebingen-2022/",
        "https://www.lpb-bw.de/praktikumsbewerbung-lpb-aussenstelle-tuebingen/",
        "https://www.lpb-tuebingen.de/",
        "https://www.lpb-tuebingen.de/as-tue-halbtaegige-va-1/",
        "https://www.lpb-tuebingen.de/fragen-politische-tage-tue/",
        "https://www.lpb-tuebingen.de/politische-tage-fuer-schulen/",
        "https://www.lpb-tuebingen/",
        "https://www.lumi-tuebingen.de/",
        "https://www.mackelab.org/tuebingen/",
        "https://www.maedchentreff-tuebingen.de/",
        "https://www.marktschenke-tuebingen.de/",
        "https://www.martinsgemeinde-tuebingen.de/",
        "https://www.medizin.uni-tuebingen.de/",
        "https://www.medizin.uni-tuebingen.de/de/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/kliniken/medizinische-klinik/innere-medizin-viii/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/kliniken/medizinische-klinik/sportmedizin/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/kliniken/medizinische-klinik/tropenmedizin/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/kliniken/medizinische-klinik/tropenmedizin/forschung/arbeitsgruppe-kreidenweiss/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/kliniken/neurologie/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/kliniken/psychiatrie-und-psychotherapie/allgemeine-psychiatrie/forschung/sektion-fuer-suchtmedizin-und-suchtforschung/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/zentren/ernaehrungsmedizin/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/zentren/geriatrisches-zentrum/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/zentren/gerinnungszentrum/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/zentren/neurosensorik-zfn/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/einrichtungen/zentren/tumorzentrum-ccc/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/mitarbeiter/profil/1627/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/mitarbeiter/profil/1924/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/mitarbeiter/profil/968/",
        "https://www.medizin.uni-tuebingen.de/de/das-klinikum/veranstaltungskalender/veranstaltung/1629/",
        "https://www.medizin.uni-tuebingen.de/de/kontakt/anreise_einrichtungen/anreise-static-content/",
        "https://www.medizin.uni-tuebingen.de/de/kontakt/parken-am-klinikum/",
        "https://www.medizin.uni-tuebingen.de/de/maennergesundheit/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/forschung/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/forschung/forschergruppen/for-2715/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/forschung/forschungsfoerderung#junior_academy/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/forschung/forschungsfoerderung/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/forschung/ifit-exzellenzcluster/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/gleichstellung/forschung-und-familie/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/gleichstellung/gleichstellungskommission/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/gleichstellung/tff-frauenfrderung/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/promotionen/phd-studiengang/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/promotionen/promotionskolleg/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/struktur-und-berufung/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/studium-und-lehre/studiengaenge/medizintechnik/",
        "https://www.medizin.uni-tuebingen.de/de/medizinische-fakultaet/studium-und-lehre/studiengaenge/molekulare-medizin/",
        "https://www.medizin.uni-tuebingen.de/de/startseite/",
        "https://www.medizin.uni-tuebingen.de/en-de/das-klinikum/einrichtungen/kliniken/psychiatrie-und-psychotherapie/allgemeine-psychiatrie/forschung/sektion-fuer-suchtmedizin-und-suchtforschung/",
        "https://www.medizin.uni-tuebingen.de/en-de/das-klinikum/einrichtungen/zentren/comprehensive-infectious-disease-center-cidic/",
        "https://www.medizin.uni-tuebingen.de/en-de/medizinische-fakultaet/",
        "https://www.medizin.uni-tuebingen.de/en-de/medizinische-fakultaet/forschung/forschergruppen/for-2715/",
        "https://www.medizin.uni-tuebingen.de/en-de/medizinische-fakultaet/forschung/ifit-exzellenzcluster/",
        "https://www.medizin.uni-tuebingen.de/en-de/startseite/",
        "https://www.medizin.uni-tuebingen.de/en/Press/Imprint.html",
        "https://www.medizin.uni-tuebingen.de/en/Press/Our+Institutions+A+_+Z/Centres/Center+for+Nutritional+Medicine+%28_ZEM_%29-port-10011-p-758.html",
        "https://www.medizin.uni-tuebingen.de/en/Research.html",
        "https://www.medizin.uni-tuebingen.de/en/Research/Collaborative+Research/IZST.html",
        "https://www.medizin.uni-tuebingen.de/en/Research/Research+Focus/Vascular+Medicine+and+Diabetes.html",
        "https://www.medizin.uni-tuebingen.de/en/Students/Faculty+of+Medicine/Executive+Board+of+the+Faculty+of+Medicine.html",
        "https://www.medizin.uni-tuebingen.de/etb/servlet/eGuide/",
        "https://www.medizin.uni-tuebingen.de/Forschung/Forschungsverb%C3%BCnde/IZST.html",
        "https://www.medizin.uni-tuebingen.de/go/kita/",
        "https://www.medizin.uni-tuebingen.de/intrafox/cgi-bin/external-wrapper.app/",
        "https://www.medizin.uni-tuebingen.de/Mitarbeiter/Karriere/Job+finden+_+Bewerben/Jobangebote.html",
        "https://www.medizin.uni-tuebingen.de/Patienten/Zentren/Tumorzentrum+CCC+T%C3%BCbingen/Tumorspezifische+Zentren/Zentrum+f%C3%BCr+Urogenitale+Tumoren.html",
        "https://www.medizin.uni-tuebingen.de/Patienten/Zentren/Tumorzentrum+CCC+T%C3%BCbingen_Stuttgart-port-80-p-762.html",
        "https://www.medizin.uni-tuebingen.de/Patienten/Zentren/Tumorzentrum+CCC+T�bingen_Stuttgart-port-10443-p-762.html",
        "https://www.medizin.uni-tuebingen.de/Presse_Aktuell/Einrichtungen+A+bis+Z/Institute/Allgemeinmedizin/Wir+%C3%BCber+uns/Newsletter.html",
        "https://www.medizin.uni-tuebingen.de/Presse_Aktuell/Einrichtungen+A+bis+Z/Kliniken/Augenheilkunde/Augenklinik/F%C3%BCr+%C3%84rztliche+Kollegen/Newsletter+f%C3%BCr+Augen%C3%A4rzte.html",
        "https://www.medizin.uni-tuebingen.de/Presse_Aktuell/Einrichtungen+A+bis+Z/Leitung+und+Verwaltung/Beauftragte+des+Klinikums/Datenschutz.html",
        "https://www.medizin.uni-tuebingen.de/Presse_Aktuell/Einrichtungen+A+bis+Z/Zentrale+Einrichtungen/Akademie.html",
        "https://www.medizin.uni-tuebingen.de/Presse_Aktuell/Einrichtungen+A+bis+Z/Zentrale+Einrichtungen/Diagnostische+Labormedizin.html",
        "https://www.medizin.uni-tuebingen.de/Presse_Aktuell/Impressum.html",
        "https://www.medizin.uni-tuebingen.de/publicETB/servlet/eGuide/",
        "https://www.medizin.uni-tuebingen.de/Studierende.html",
        "https://www.medizin.uni-tuebingen.de/Studierende/Medizindidaktik+.html",
        "https://www.medizin.uni-tuebingen.de/Studierende/Medizinische+Fakult%C3%A4t/Dekanat+%28Fakult%C3%A4tsvorstand%29.html",
        "https://www.mein-check-in.de/kreis-tuebingen/",
        "https://www.mein-check-in.de/tuebingen/ausbildung/",
        "https://www.mein-check-in.de/tuebingen/overview/",
        "https://www.mein-check-in.de/tuebingen/padagogischerbereich/",
        "https://www.mein-check-in.de/tuebingen/stellenangebote/",
        "https://www.meinprospekt.de/staedte/tuebingen/angebote/",
        "https://www.meinprospekt.de/tuebingen/aldisued-de/",
        "https://www.meinprospekt.de/tuebingen/alnatura-de/",
        "https://www.meinprospekt.de/tuebingen/angebote/bier/",
        "https://www.meinprospekt.de/tuebingen/angebote/bitburger/",
        "https://www.meinprospekt.de/tuebingen/angebote/coca-cola/",
        "https://www.meinprospekt.de/tuebingen/angebote/fernseher/",
        "https://www.meinprospekt.de/tuebingen/angebote/feuerwerk/",
        "https://www.meinprospekt.de/tuebingen/angebote/havana-club/",
        "https://www.meinprospekt.de/tuebingen/angebote/jack-daniels/",
        "https://www.meinprospekt.de/tuebingen/angebote/kaffee/",
        "https://www.meinprospekt.de/tuebingen/angebote/krombacher/",
        "https://www.meinprospekt.de/tuebingen/angebote/red-bull/",
        "https://www.meinprospekt.de/tuebingen/angebote/rotkaeppchen-sekt/",
        "https://www.meinprospekt.de/tuebingen/angebote/veltins/",
        "https://www.meinprospekt.de/tuebingen/angebote/volvic/",
        "https://www.meinprospekt.de/tuebingen/angebote/waschmaschine/",
        "https://www.meinprospekt.de/tuebingen/angebote/weihnachtsbaum/",
        "https://www.meinprospekt.de/tuebingen/apotheken/",
        "https://www.meinprospekt.de/tuebingen/auto-motorrad/",
        "https://www.meinprospekt.de/tuebingen/awg-de/",
        "https://www.meinprospekt.de/tuebingen/baeckerein/",
        "https://www.meinprospekt.de/tuebingen/banken/",
        "https://www.meinprospekt.de/tuebingen/baumaerkte/",
        "https://www.meinprospekt.de/tuebingen/biomaerkte/",
        "https://www.meinprospekt.de/tuebingen/buchhandlungen/",
        "https://www.meinprospekt.de/tuebingen/depot-de/",
        "https://www.meinprospekt.de/tuebingen/dienstleister/",
        "https://www.meinprospekt.de/tuebingen/discounter/",
        "https://www.meinprospekt.de/tuebingen/dm-de/",
        "https://www.meinprospekt.de/tuebingen/drogerien/",
        "https://www.meinprospekt.de/tuebingen/edeka/",
        "https://www.meinprospekt.de/tuebingen/edekacenter-de/",
        "https://www.meinprospekt.de/tuebingen/ein-euro-maerkte/",
        "https://www.meinprospekt.de/tuebingen/euronics-de/",
        "https://www.meinprospekt.de/tuebingen/fast-food/",
        "https://www.meinprospekt.de/tuebingen/filialen/",
        "https://www.meinprospekt.de/tuebingen/filialen/aldisued-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/aldisued-de/28075/",
        "https://www.meinprospekt.de/tuebingen/filialen/alnatura-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/awg-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/awg-de/29789/",
        "https://www.meinprospekt.de/tuebingen/filialen/bonita/",
        "https://www.meinprospekt.de/tuebingen/filialen/bonita/553963/",
        "https://www.meinprospekt.de/tuebingen/filialen/depot-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/deutsche-post/",
        "https://www.meinprospekt.de/tuebingen/filialen/dhl-packstation/",
        "https://www.meinprospekt.de/tuebingen/filialen/dhl-paketshop/",
        "https://www.meinprospekt.de/tuebingen/filialen/dhl-paketshop/493129/",
        "https://www.meinprospekt.de/tuebingen/filialen/dm-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/edeka/",
        "https://www.meinprospekt.de/tuebingen/filialen/edekacenter-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/euronics-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/hermes-paketshop/",
        "https://www.meinprospekt.de/tuebingen/filialen/kaufland/",
        "https://www.meinprospekt.de/tuebingen/filialen/lidl/",
        "https://www.meinprospekt.de/tuebingen/filialen/lidl/153126/",
        "https://www.meinprospekt.de/tuebingen/filialen/nahundgut-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/penny-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/rewe-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/saturn-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/vitalia-de/",
        "https://www.meinprospekt.de/tuebingen/filialen/vw-de/",
        "https://www.meinprospekt.de/tuebingen/fotofachgeschaefte/",
        "https://www.meinprospekt.de/tuebingen/gartencenter/",
        "https://www.meinprospekt.de/tuebingen/getraenkemaerkte/",
        "https://www.meinprospekt.de/tuebingen/kaufhaeuser/",
        "https://www.meinprospekt.de/tuebingen/kaufland/",
        "https://www.meinprospekt.de/tuebingen/lidl/",
        "https://www.meinprospekt.de/tuebingen/marken/",
        "https://www.meinprospekt.de/tuebingen/modehaeuser/",
        "https://www.meinprospekt.de/tuebingen/moebelhaeuser/",
        "https://www.meinprospekt.de/tuebingen/nahundgut-de/",
        "https://www.meinprospekt.de/tuebingen/optiker/",
        "https://www.meinprospekt.de/tuebingen/parfuemerien-beauty/",
        "https://www.meinprospekt.de/tuebingen/penny-de/",
        "https://www.meinprospekt.de/tuebingen/reisen/",
        "https://www.meinprospekt.de/tuebingen/rewe-de/",
        "https://www.meinprospekt.de/tuebingen/sanitaetshaeuser/",
        "https://www.meinprospekt.de/tuebingen/saturn-de/",
        "https://www.meinprospekt.de/tuebingen/schreibwaren-buerobedarf/",
        "https://www.meinprospekt.de/tuebingen/schuhgeschaefte/",
        "https://www.meinprospekt.de/tuebingen/spielzeug-baby/",
        "https://www.meinprospekt.de/tuebingen/sportgeschaefte/",
        "https://www.meinprospekt.de/tuebingen/supermaerkte/",
        "https://www.meinprospekt.de/tuebingen/tankstellen/",
        "https://www.meinprospekt.de/tuebingen/technikmaerkte/",
        "https://www.meinprospekt.de/tuebingen/uhren-schmuck/",
        "https://www.meinprospekt.de/tuebingen/vitalia-de/",
        "https://www.meinprospekt.de/tuebingen/vw-de/",
        "https://www.meinprospekt.de/tuebingen/weitere-geschaefte/",
        "https://www.meinprospekt.de/tuebingen/zoohandlungen/",
        "https://www.mey-generalbau-triathlon.com/news/nahezu-ausverkauft-mey-generalbau-triathlon-tubingen-vor-grandiosem-comeback/",
        "https://www.mey-generalbau-triathlon.com/news/tubingen-fiebert-dem-comeback-des-mey-generalbau-triathlon-entgegen/",
        "https://www.mietspiegel-tuebingen.de/",
        "https://www.minube.net/guides/germany/baden-wurttemberg/tubingen/",
        "https://www.minube.net/photos/tubingen-c216356/",
        "https://www.minube.net/place/hohentubingen-castle--a8284/",
        "https://www.minube.net/place/jardin-botanico-de-tubingen--a940881/",
        "https://www.minube.net/place/renaissance-town-hall-of-tubingen--a8286/",
        "https://www.minube.net/place/schloss-hohentubingen-hillclimb--a587221/",
        "https://www.minube.net/place/tubingen-alterstadt--a582441/",
        "https://www.minube.net/place/viewpoint-park-hohentubingen--a587231/",
        "https://www.minube.net/restaurants/germany/baden-wurttemberg/tubingen/",
        "https://www.minube.net/tag/castles-tubingen-c216356/",
        "https://www.minube.net/tag/churches-tubingen-c216356/",
        "https://www.minube.net/tag/cities-tubingen-c216356/",
        "https://www.minube.net/tag/of-touristic-interest-tubingen-c216356/",
        "https://www.minube.net/tag/squares-tubingen-c216356/",
        "https://www.minube.net/tag/streets-tubingen-c216356/",
        "https://www.minube.net/travel/germany/baden-wurttemberg/tubingen/",
        "https://www.minube.net/where-to-stay/germany/baden-wurttemberg/tubingen/",
        "https://www.mokka-in-tuebingen.de/",
        "https://www.mokka-tuebingen.de/",
        "https://www.morejoe.de/tuebingen-tasse.html",
        "https://www.mozzarellabar-tuebingen.de/",
        "https://www.museumsgesellschaft-tuebingen.de/",
        "https://www.my-stuwe.de/kita/kita-tuebingen/",
        "https://www.my-stuwe.de/kita/tuebingen/",
        "https://www.my-stuwe.de/mensa/cafeteria-clubhaus-tuebingen/",
        "https://www.my-stuwe.de/mensa/cafeteria-morgenstelle-tuebingen/",
        "https://www.my-stuwe.de/mensa/cafeteria-neuphilologicum-tuebingen/",
        "https://www.my-stuwe.de/mensa/cafeteria-theologicum-tuebingen/",
        "https://www.my-stuwe.de/mensa/cafeteria-unibibliothek-tuebingen/",
        "https://www.my-stuwe.de/mensa/mensa-morgenstelle-tuebingen/",
        "https://www.my-stuwe.de/mensa/mensa-prinz-karl-tuebingen/",
        "https://www.my-stuwe.de/weihnachtsessen-in-unseren-mensen-tuebingen-und-reutlingen/",
        "https://www.my-stuwe.de/wohnen/wohnheime-tuebingen/",
        "https://www.mygermanyvacation.com/ibis-styles-tuebingen-tbingen-updated-2023-prices/",
        "https://www.mygermanyvacation.com/tag/tubingen/",
        "https://www.nabu-tuebingen.de/",
        "https://www.nabu-tuebingen.de/2023/04/12/radtour-zu-den-nabu-biotopen-am-22-04/",
        "https://www.nabu-tuebingen.de/2023/04/12/vogelf%C3%BChrung-nachtigall-am-28-04/",
        "https://www.nabu-tuebingen.de/2023/04/12/vogelf�hrung-nachtigall-am-28-04/",
        "https://www.nabu-tuebingen.de/2023/04/17/amphibien-am-spitzberg-exkursion-f%C3%BCr-kinder-6-bis-12-jahre/",
        "https://www.nabu-tuebingen.de/2023/04/17/amphibien-am-spitzberg-exkursion-f�r-kinder-6-bis-12-jahre/",
        "https://www.nabu-tuebingen.de/2023/04/18/vortrag-vogelvielfalt-in-und-um-t%C3%BCbingen/",
        "https://www.nabu-tuebingen.de/2023/04/18/vortrag-vogelvielfalt-in-und-um-t�bingen/",
        "https://www.nabu-tuebingen.de/2023/05/04/schmetterlingsf%C3%BChrung-in-b%C3%BChl/",
        "https://www.nabu-tuebingen.de/2023/05/04/schmetterlingsf�hrung-in-b�hl/",
        "https://www.nabu-tuebingen.de/2023/05/04/vortrag-geschichten-%C3%BCber-erstaunliche-f%C3%A4higkeiten-und-lebensweisen-einzelner-vogelarten/",
        "https://www.nabu-tuebingen.de/2023/05/04/vortrag-geschichten-�ber-erstaunliche-f�higkeiten-und-lebensweisen-einzelner-vogelarten/",
        "https://www.nabu-tuebingen.de/2023/06/02/60-nester-f%C3%BCr-mauersegler/",
        "https://www.nabu-tuebingen.de/2023/06/02/60-nester-f�r-mauersegler/",
        "https://www.nabu-tuebingen.de/2023/06/02/jahreshauptversammlung/",
        "https://www.nabu-tuebingen.de/2023/06/22/fotoausstellung-szenen-aus-unserer-vogelwelt/",
        "https://www.nabu-tuebingen.de/2023/07/13/schmetterlingsf%C3%BChrung-am-alten-berg/",
        "https://www.nabu-tuebingen.de/2023/07/13/schmetterlingsf�hrung-am-alten-berg/",
        "https://www.nachbarschaftsverband-reutlingen-tuebingen.de/",
        "https://www.nak-albstadt-tuebingen.de/tuebingen/",
        "https://www.nak-tuebingen.de/",
        "https://www.naturfreunde-tuebingen.de/",
        "https://www.naturpark-schoenbuch.de/aktuell/neue-rad-und-wanderkarte-fuer-naturpark-schoenbuch-und-kreis-tuebingen/",
        "https://www.nc-werte.info/hochschule/uni-tuebingen/sport-sportpublizistik/",
        "https://www.neuroschool-tuebingen.de/",
        "https://www.nightline-tuebingen.de/",
        "https://www.nikolauslauf-tuebingen.de/",
        "https://www.nusser-schaal.de/tuebingen/",
        "https://www.o2-tuebingen.de/",
        "https://www.obi.de/markt/tuebingen/",
        "https://www.occ-tuebingen.de/",
        "https://www.occ-tuebingen.de/aerzte/amei-roehner-zangiabadi/",
        "https://www.occ-tuebingen.de/aerzte/angestellte-aerzte/dr-gudrun-schanz/",
        "https://www.occ-tuebingen.de/aerzte/angestellte-aerzte/dr-philipp-calgeer/",
        "https://www.occ-tuebingen.de/aerzte/angestellte-aerzte/jonas-hoffmann/",
        "https://www.occ-tuebingen.de/aerzte/dr-andreas-mehling/",
        "https://www.occ-tuebingen.de/aerzte/dr-bernhard-schewe/",
        "https://www.occ-tuebingen.de/aerzte/dr-juergen-fritz/",
        "https://www.occ-tuebingen.de/aerzte/prof-dr-philip-kasten/",
        "https://www.occ-tuebingen.de/aktuelles/praxisurlaub/",
        "https://www.occ-tuebingen.de/chirurgie/gefaessmedizin/krampfadern/",
        "https://www.occ-tuebingen.de/chirurgie/lipoedem/",
        "https://www.occ-tuebingen.de/orthopaedie/ellenbogen/",
        "https://www.occ-tuebingen.de/orthopaedie/knie/",
        "https://www.occ-tuebingen.de/orthopaedie/schulter/",
        "https://www.occ-tuebingen.de/orthopaedie/sprunggelenk-fuss/",
        "https://www.opel-lindenschmid-tuebingen.de/",
        "https://www.optikfischertuebingen.de/",
        "https://www.outdooractive.com/en/accessibility/tuebingen/accessible-holidays-in-tuebingen/202373135/",
        "https://www.outdooractive.com/en/accommodation/tuebingen/accommodation-in-tuebingen/8246580/",
        "https://www.outdooractive.com/en/dog-friendly-hiking/tuebingen/dog-friendly-holidays-in-tuebingen/205246585/",
        "https://www.outdooractive.com/en/great-places-to-visit-with-the-family/tuebingen/family-holidays-in-tuebingen/202373138/",
        "https://www.outdooractive.com/en/huts/tuebingen/mountain-huts-in-tuebingen/8246579/",
        "https://www.outdooractive.com/en/ideas-for-bad-weather/tuebingen/bad-weather-activities-in-tuebingen/202373137/",
        "https://www.outdooractive.com/en/natural-monuments/tuebingen/natural-monuments-in-tuebingen/21858814/",
        "https://www.outdooractive.com/en/places-to-eat-drink/tuebingen/eat-drink-in-tuebingen/21876961/",
        "https://www.outdooractive.com/en/places-to-see/tuebingen/landscape-in-tuebingen/21873367/",
        "https://www.outdooractive.com/en/poi/schwaebische-alb/botanischer-garten-der-universitaetsstadt-tuebingen-die-vielfalt-des/8767313/",
        "https://www.outdooractive.com/en/poi/schwaebische-alb/neckarinsel-tuebingen/14672287/",
        "https://www.outdooractive.com/en/travel-guide/germany/tuebingen/1022199/",
        "https://www.outdooractive.com/en/viewpoints/tuebingen/viewpoints-in-tuebingen/21858813/",
        "https://www.outdooractive.com/en/webcams/tuebingen/webcams-in-tuebingen/227976604/",
        "https://www.pestalozzischule-tuebingen.de/",
        "https://www.pflegedienst-tuebingen.de/",
        "https://www.polizei-tuebingen.de/",
        "https://www.post-sv-tuebingen.de/",
        "https://www.post-sv-tuebingen.de/index.php/laufen-nordic-walking/96-laufveranstaltungen/1304-frankfurt-marathon-nikolauslauf-siegerin-beste-deutsche-merle-brunnee-mit-neuer-bestzeit/",
        "https://www.post-sv-tuebingen.de/index.php/laufen-nordic-walking/96-laufveranstaltungen/1364-tag-des-laufens-am-7-juni-laeuft-ganz-deutschland-fuer-die-rettung-des-waldes-wir-auch/",
        "https://www.post-sv-tuebingen.de/index.php/sportabzeichen/",
        "https://www.praeventionssport-tuebingen.de/",
        "https://www.praxisportal.uni-tuebingen.de/",
        "https://www.praxisportal.uni-tuebingen.de/signin/",
        "https://www.profamilia.de/angebote-vor-ort/baden-wuerttemberg/tuebingen/",
        "https://www.profamilia.de/tuebingen/",
        "https://www.prophysio-tuebingen.de/",
        "https://www.pusteblume-tuebingen.de/",
        "https://www.qnb-tuebingen.de/",
        "https://www.qnb-tuebingen.de/expertensuche/",
        "https://www.radlager-tuebingen.de/",
        "https://www.radundtattuebingen.de/",
        "https://www.raktuebingen.de/",
        "https://www.raktuebingen.de/auszubildende/",
        "https://www.raktuebingen.de/auszubildende/formulare/",
        "https://www.raktuebingen.de/auszubildende/rechtsanwaltsfachangestellte/",
        "https://www.raktuebingen.de/auszubildende/rechtsfachwirte/",
        "https://www.raktuebingen.de/buerger/anwaltssuche/bundesverzeichnis/",
        "https://www.raktuebingen.de/buerger/anwaltssuche/online/",
        "https://www.raktuebingen.de/buerger/anwaltssuche/pflichtverteidigersuche/",
        "https://www.raktuebingen.de/buerger/anwaltssuche/telefon/",
        "https://www.raktuebingen.de/buerger/beschwerden/",
        "https://www.raktuebingen.de/buerger/infos/",
        "https://www.raktuebingen.de/buerger/schlichtungsverfahren/",
        "https://www.raktuebingen.de/downloads/formulare/",
        "https://www.raktuebingen.de/downloads/kammerreport/",
        "https://www.raktuebingen.de/downloads/satzungen/",
        "https://www.raktuebingen.de/fortbildungen/",
        "https://www.raktuebingen.de/kontakt/",
        "https://www.raktuebingen.de/rak/",
        "https://www.raktuebingen.de/rak/aktuelle-mitteilungen/",
        "https://www.raktuebingen.de/rak/geschaeftsstelle-2/",
        "https://www.raktuebingen.de/rak/vorstand/",
        "https://www.raktuebingen.de/rak/vorstandswahl2022/",
        "https://www.raktuebingen.de/rechtsanwaelte/bea/aktive-nutzungspflicht/",
        "https://www.raktuebingen.de/rechtsanwaelte/bea/infos/",
        "https://www.raktuebingen.de/rechtsanwaelte/bea/kartenbestellung/",
        "https://www.raktuebingen.de/rechtsanwaelte/bea/kartentausch-2022/",
        "https://www.raktuebingen.de/rechtsanwaelte/beruf-und-pflichte/",
        "https://www.raktuebingen.de/rechtsanwaelte/berufsausuebungsgesellschaften/",
        "https://www.raktuebingen.de/rechtsanwaelte/datenschutz/",
        "https://www.raktuebingen.de/rechtsanwaelte/fachanwaltschaften/",
        "https://www.raktuebingen.de/rechtsanwaelte/gwg/",
        "https://www.raktuebingen.de/rechtsanwaelte/news/",
        "https://www.raktuebingen.de/rechtsanwaelte/syndikusrechtsanwaelte/",
        "https://www.raktuebingen.de/rechtsanwaelte/vdb/formulare/",
        "https://www.raktuebingen.de/rechtsanwaelte/vdb/infos/",
        "https://www.raktuebingen.de/rechtsanwaelte/vdb/leitfaden/",
        "https://www.raktuebingen.de/rechtsanwaelte/zulassung/",
        "https://www.raktuebingen.de/stellen/aktuelle-stellen/",
        "https://www.raktuebingen.de/stellen/angebote/",
        "https://www.raktuebingen.de/stellen/gesuche/",
        "https://www.ratskeller-tuebingen.com/",
        "https://www.reisebuero-uebersee.de/tuebingen/",
        "https://www.reparaturfuehrer-tuebingen.de/",
        "https://www.reservix.de/tuebingen/venue/casino-tuebingen/v2972/",
        "https://www.reservix.de/tuebingen/venue/festplatz-tuebingen/v2984/",
        "https://www.reservix.de/tuebingen/venue/japengo/v35312/",
        "https://www.reservix.de/tuebingen/venue/kloster-bebenhausen/v3065/",
        "https://www.reservix.de/tuebingen/venue/loewen-tuebingen/v3038/",
        "https://www.reservix.de/tuebingen/venue/schloss-hohentuebingen/v3009/",
        "https://www.reservix.de/tuebingen/venue/shedhalle-tuebingen/v3067/",
        "https://www.reservix.de/tuebingen/venue/sparkassen-carre/v2967/",
        "https://www.reservix.de/tuebingen/venue/sudhaus/v2949/",
        "https://www.retour-tuebingen.de/",
        "https://www.reusch-tuebingen.de/",
        "https://www.rewe.de/angebote/tuebingen/840212/rewe-markt-schleifmuehleweg-36/",
        "https://www.risiko-tuebingen.de/",
        "https://www.riva-tuebingen.de/",
        "https://www.rp-tuebingen.de/",
        "https://www.rp-tuebingen.de/servlet/PB/menu/1007467_l1/index.html",
        "https://www.safran-tuebingen.de/",
        "https://www.samariterstiftung.de/standorte/altenpflege/tuebingen/diakoniestation-tuebingen.html",
        "https://www.scenario-tuebingen.de/",
        "https://www.schornsteinfeger-innung-tuebingen.de/",
        "https://www.schulamt-tuebingen.de/",
        "https://www.schummeltag-streetfood.de/event/street-food-festival-tuebingen-2021/",
        "https://www.schwarz-architektur-tuebingen.de/",
        "https://www.scientists4future.org/mitmachen/regionalgruppen/rg-tuebingen/",
        "https://www.self-assessment.uni-tuebingen.de/",
        "https://www.self-assessment.uni-tuebingen.de/index.php/",
        "https://www.seminar-tuebingen.de/",
        "https://www.seminar-tuebingen.de/,Lde/Startseite/",
        "https://www.sfs-tuebingen.de/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/events/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/genussfuehrer/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/kochabende/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/kontakt/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/literarische-lesungen/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/rg-unterstuetzer/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/rueckblick_2016/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/rueckblick_2017/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/rueckblick_2018/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/rueckblick_2019/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/rueckblick_bis_2015/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/schneckentische/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/termine/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/unterstuetzer/",
        "https://www.slowfood.de/netzwerk/vor-ort/tuebingen/weinbau/",
        "https://www.sozialforum-tuebingen.de/",
        "https://www.sozialforum-tuebingen.de/cms-verein/-sozialforum-patientenforum-/-sozialforum-patientenforum.html",
        "https://www.spatzennest-tuebingen.de/",
        "https://www.spiegel.de/panorama/leute/boris-palmer-gewinnt-oberbuergermeister-wahl-in-tuebingen-palmer-oder-nichts-a-3c22c3f0-8eb8-461f-bd74-e68309c4f4ff/",
        "https://www.sport2000.de/stores/tuebingen/",
        "https://www.sportkreis-tuebingen.de/",
        "https://www.srg-tuebingen.de/",
        "https://www.st-michael-tuebingen.de/",
        "https://www.stadtseniorenrat-tuebingen.de/",
        "https://www.stadtseniorenrat-tuebingen.de/aktuelles/",
        "https://www.stadtseniorenrat-tuebingen.de/beratung-heimbeiraete/",
        "https://www.stadtseniorenrat-tuebingen.de/cookie-richtlinie-eu/",
        "https://www.stadtseniorenrat-tuebingen.de/datenschutz/",
        "https://www.stadtseniorenrat-tuebingen.de/generationengerechter-einkauf/",
        "https://www.stadtseniorenrat-tuebingen.de/impressum/",
        "https://www.stadtseniorenrat-tuebingen.de/kontakt/",
        "https://www.stadtseniorenrat-tuebingen.de/links/",
        "https://www.stadtseniorenrat-tuebingen.de/literatur-am-nachmittag/",
        "https://www.stadtseniorenrat-tuebingen.de/mediation/",
        "https://www.stadtseniorenrat-tuebingen.de/mitarbeit/",
        "https://www.stadtseniorenrat-tuebingen.de/naherholung-2018-2/",
        "https://www.stadtseniorenrat-tuebingen.de/netzwerk-demenz/",
        "https://www.stadtseniorenrat-tuebingen.de/optiwohn/",
        "https://www.stadtseniorenrat-tuebingen.de/patientenforum-tuebingen/",
        "https://www.stadtseniorenrat-tuebingen.de/patientenverfuegung/",
        "https://www.stadtseniorenrat-tuebingen.de/rechtsberatung/",
        "https://www.stadtseniorenrat-tuebingen.de/seniorenclubs/",
        "https://www.stadtseniorenrat-tuebingen.de/stadtteiltreffs/",
        "https://www.stadtseniorenrat-tuebingen.de/unterwegs-ins-aelterwerden-2/",
        "https://www.stadtseniorenrat-tuebingen.de/unterwegs-ins-aelterwerden/",
        "https://www.stadtseniorenrat-tuebingen.de/verein/",
        "https://www.stadtseniorenrat-tuebingen.de/verein/geschichte/",
        "https://www.stadtseniorenrat-tuebingen.de/verein/ueber-uns/",
        "https://www.stadtseniorenrat-tuebingen.de/verein/vorstand/",
        "https://www.stadtseniorenrat-tuebingen.de/vorsorgevollmacht/",
        "https://www.stadtseniorenrat-tuebingen.de/wegweiser-2018/",
        "https://www.stadtseniorenrat-tuebingen.de/wohnberatung/",
        "https://www.stadtseniorenrat-tuebingen.de/wp-login.php/",
        "https://www.staerke-kreis-tuebingen.de/",
        "https://www.stern-tuebingen.de/",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/basketball--tigers-tuebingen-holen-basketballer-jackson-33671216.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/basketball--tigers-tuebingen-verpflichten-basketballer-darko-kelly-33604884.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/basketball-bundesliga--tigers-tuebingen-verlaengern-mit-basketballer-ersek-33582668.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/basketball-bundesliga--tigers-tuebingen-verpflichten-james-boeheim-33621350.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/ruecksicht--tuebingen-erhoeht-bussgelder-fuer-achtlos-weggeworfenen-muell-33639062.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/sport--tuebingen-kehrt-in-die-basketball-bundesliga-zurueck-33619872.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/tuebingen--boris-palmer-tritt-nach-auszeit-wieder-oeffentlich-auf-33606920.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/tuebingen--forschungszentrum-fuer-ki-spitzenforschung-gegruendet-33662406.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/tuebingen--nach-leichenfund--frueherer-lebensgefaehrte-in-u-haft-33579184.html",
        "https://www.stern.de/gesellschaft/regional/baden-wuerttemberg/tuebingen--sechs-verletzte-bei-auffahrunfall-mit-vier-fahrzeugen-33648750.html",
        "https://www.stern.de/gesundheit/corona-schnelltest--tuebingen-lockt-menschen-zum-shoppen-in-die-innenstadt--video--30434720.html",
        "https://www.stern.de/gesundheit/modellprojekt--tuebingen-haelt-an-der-idee-der-neuen-freiheit-fest---trotz-steigender-inzidenz-30456530.html",
        "https://www.stern.de/gesundheit/palmers-corona-sonderweg--tuebingen-will-ab-kommender-woche-wieder-kinos--museen-und-aussengastronomie-oeffnen-30432036.html",
        "https://www.stern.de/news/oberbuergermeisterwahl-in-tuebingen-entscheidet-ueber-politische-zukunft-palmers-32841368.html",
        "https://www.stern.de/panorama/erdbeben-fuehrt-zu-spuerbaren-erschuetterungen-suedlich-von-tuebingen-32819730.html",
        "https://www.stern.de/panorama/prozess-in-tuebingen--sechsjaehrige-tochter-zu-sex-dates-mitgenommen--haftstrafen-33603006.html",
        "https://www.stern.de/panorama/verbrechen/tuebingen--6-jaehrige-musste-laut-anklage-sex-treffen-der-mutter-filmen-33576194.html",
        "https://www.stern.de/politik/deutschland/boris-palmer-bleibt-oberbuergermeister-von-tuebingen-32842910.html",
        "https://www.stern.de/politik/deutschland/boris-palmer-tritt-bei-ob-wahl-in-tuebingen-als-unabhaengiger-kandidat-an-31583252.html",
        "https://www.stern.de/politik/deutschland/die-morgenlage--tuebingens-ob-boris-palmer-wirft-gruenen--ausgrenzung--vor-30519802.html",
        "https://www.stern.de/politik/deutschland/themen/tuebingen-4161038.html",
        "https://www.stern.de/politik/deutschland/tuebingen--ob-boris-palmer-beschliesst-hoehere-parkgebuehren-fuer-suv-fahrer-30760424.html",
        "https://www.stern.de/politik/deutschland/wenn-sich-normalitaet-wie-urlaub-anfuehlt---unser-autor-ist-in-die-modellstadt-tuebingen-gefahren-30456854.html",
        "https://www.stiftskirche-tuebingen.de/",
        "https://www.stiftskirche-tuebingen.de/gemeindeleben/luv-in-6-einheiten-tiefer-ins-leben-eintauchen/",
        "https://www.stiftskirche-tuebingen.de/gottesdienste/lessons/",
        "https://www.stiftskirche-tuebingen.de/gottesdienste/motette/",
        "https://www.stiftskirche-tuebingen.de/kirchenmusik/orgelsommer/",
        "https://www.stiftskirche-tuebingen.de/meta/datenschutz/",
        "https://www.stiftskirche-tuebingen.de/ueber-uns/ansprechpartnerinnen#c1264948/",
        "https://www.stiftungsverzeichnis-bw.de/tuebingen/",
        "https://www.studis-online.de/hochschulen/uni-tuebingen/",
        "https://www.studis-online.de/hochschulen/uni-tuebingen/lehramt/gymnasium/",
        "https://www.studis-online.de/hochschulen/uni-tuebingen/studiengaenge/",
        "https://www.stura-tuebingen.de/",
        "https://www.stura-tuebingen.de/abrechnung-fachschaften-doktorandenkonvente/",
        "https://www.stura-tuebingen.de/aktuelle-tagesordnung/",
        "https://www.stura-tuebingen.de/aktuelles/",
        "https://www.stura-tuebingen.de/arbeitskreise/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-auslaendische-studierende/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-beeintraechtigung-und-chronische-erkrankung/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-cafeteria/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-campus-der-zukunft/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-civis/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-diesalternativer-dies-aldi/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-digitalisierung/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-familienfreundliche-hochschule/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-finanzen/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-gleichstellunggleichfilm/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-hochschulsport/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-personal/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-polbil/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-presse-und-oeffentlichkeitsarbeit/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-qualitaetssicherungsmittel/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-ract/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-raetebaubrigade/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-raetecafe/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-soziales-und-studentenwerk/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-systemakkreditierung/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-tuemaenia/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-ueberregional/",
        "https://www.stura-tuebingen.de/arbeitskreise/ak-umwelt/",
        "https://www.stura-tuebingen.de/cat/blog/pressemitteilungen/",
        "https://www.stura-tuebingen.de/datenschutz/",
        "https://www.stura-tuebingen.de/downloads/",
        "https://www.stura-tuebingen.de/en/",
        "https://www.stura-tuebingen.de/exekutivorgan/",
        "https://www.stura-tuebingen.de/fho/",
        "https://www.stura-tuebingen.de/foerderung/",
        "https://www.stura-tuebingen.de/foerderung/notlagenhilfe/",
        "https://www.stura-tuebingen.de/geschaeftsordnung/",
        "https://www.stura-tuebingen.de/hauptamtliches-prorektorat-studium-und-lehre/",
        "https://www.stura-tuebingen.de/impressum/",
        "https://www.stura-tuebingen.de/kontakt/",
        "https://www.stura-tuebingen.de/qsm-vergabe-2023/",
        "https://www.stura-tuebingen.de/satzung/",
        "https://www.stura-tuebingen.de/seminarkostenerstattung/",
        "https://www.stura-tuebingen.de/stellenangebote/",
        "https://www.stura-tuebingen.de/stellungnahmen/",
        "https://www.stura-tuebingen.de/studentische-vollversammlung-14-11-2018/",
        "https://www.stura-tuebingen.de/studentische-vollversammlung-2/",
        "https://www.stura-tuebingen.de/studentische-vollversammlung-am-10-11-2022/",
        "https://www.stura-tuebingen.de/studentische-vollversammlung-am-17-03-2022/",
        "https://www.stura-tuebingen.de/studentische-vollversammlung-wintersemester-20-21/",
        "https://www.stura-tuebingen.de/studentische-vollversammlungen/",
        "https://www.stura-tuebingen.de/studvv23/",
        "https://www.stura-tuebingen.de/stura-sitzungen/",
        "https://www.stura-tuebingen.de/stura1/",
        "https://www.stura-tuebingen.de/termine/kategorie/stura-sitzung/liste/",
        "https://www.stura-tuebingen.de/termine/monat/",
        "https://www.stura-tuebingen.de/transparenz-der-studienleistungen/",
        "https://www.stura-tuebingen.de/ueber-uns/",
        "https://www.stura-tuebingen.de/ueber-uns/das-pressereferat/",
        "https://www.stura-tuebingen.de/ueber-uns/mitgliedschaften/",
        "https://www.stura-tuebingen.de/ueber-uns/referat-soziales-und-gleichstellung/",
        "https://www.stura-tuebingen.de/ueber-uns/referat-studium-und-lehre/",
        "https://www.stura-tuebingen.de/ueber-uns/referat-umwelt-und-politische-bildung/",
        "https://www.stura-tuebingen.de/wahlen-2023/",
        "https://www.stura-tuebingen.de/wahlen-2023/infos-fuerwahlhelferinnen/",
        "https://www.stura-tuebingen.de/wer-sitzt-im-stura/",
        "https://www.stuwe-tuebingen.de/",
        "https://www.sudhaus-tuebingen.de/",
        "https://www.sudhaus-tuebingen.de/impressum.html",
        "https://www.sudhaus-tuebingen.de/kontakt/datenschutz.html",
        "https://www.sueddeutsche.de/meinung/boris-palmer-tuebingen-wahlsieger-die-gruenen-1.5680372/",
        "https://www.sueddeutsche.de/wirtschaft/bosch-ki-stadt-tuebingen-1.4519416/",
        "https://www.sueddeutsche.de/wirtschaft/verpackungssteuer-tuebingen-palmer-mcdonald-s-1.5557734/",
        "https://www.susanne-baecher.de/tuebingen-memo/",
        "https://www.susanne-baecher.de/tuebingen-quartett/",
        "https://www.sv03-tuebingen.de/fussball/",
        "https://www.swimrun-tuebingen.de/",
        "https://www.swr.de/landesschau-aktuell/bw/tuebingen/-/id=1602/f40k9y/index.html",
        "https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/index.html",
        "https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/konzilstag-in-dioezese-rottenburg-fordert-reformen-100.html",
        "https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/therapie-fuer-thrombosen-bei-astrazeneca-100.html",
        "https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/tuebingen-steuert-auf-finanzkrise-zu-und-muss-sparen-100.html",
        "https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/wahlen-in-den-usa-mit-portraits-aus-tuebingen-100.html",
        "https://www.swtue.de/baeder/freibad/70-jahre-freibad-tuebingen.html",
        "https://www.swtue.de/e-mobilitaet/ladestationen-in-tuebingen.html",
        "https://www.swtue.de/e-mobilitaet/ladestationen-in-tuebingen.html#c14850/",
        "https://www.swtue.de/e-mobilitaet/ladestationen-in-tuebingen.html#c21625/",
        "https://www.swtue.de/e-mobilitaet/ladestationen-in-tuebingen.html#meta-tab-3/",
        "https://www.swtue.de/unternehmen/aktuell/neuigkeiten/detail/am-11-april-beginnen-die-stadtwerke-tuebingen-mit-der-sanierung-im-parkhaus-altstadt-koenig.html",
        "https://www.swtue.de/unternehmen/aktuell/neuigkeiten/detail/mehr-als-qualitaet-zu-fairen-preisen-stadtwerke-tuebingen-sind-top-lokalversorger-2023.html",
        "https://www.swtue.de/unternehmen/karriere/arbeitgeber-stadtwerke-tuebingen.html",
        "https://www.swtue.de/unternehmen/karriere/arbeitgeber-stadtwerke-tuebingen.html#c20369/",
        "https://www.swtue.de/unternehmen/karriere/arbeitgeber-stadtwerke-tuebingen/wir-bieten.html",
        "https://www.swtue.de/unternehmen/presse/pressemitteilungen/detail/ein-best-place-to-learn-fuer-junge-menschen-ausbildung-der-stadtwerke-tuebingen-zertifiziert.html",
        "https://www.systemisches-institut-tuebingen.de/de/home/",
        "https://www.targetpartners.de/news/techbrunch-tuebingen-2019/",
        "https://www.tatami-restaurant-tuebingen.de/",
        "https://www.teilauto-tuebingen.de/tarife/ermaessigter-tarif/",
        "https://www.tfrt.de/technologiegebaude-uberblick/technologiegebaude-tubingen/",
        "https://www.tierschutzverein-tuebingen.de/",
        "https://www.tif-tuebingen.de/",
        "https://www.tml.cs.uni-tuebingen.de/team/luxburg/",
        "https://www.tml.cs.uni-tuebingen.de/team/luxburg/index.php/",
        "https://www.toastmasters-tuebingen.de/",
        "https://www.tourism-bw.com/attractions/museum-der-universitaet-tuebingen-mut-alte-kulturen-52732dcb08/",
        "https://www.tourismus-bw.de/attraktionen/museum-der-universitaet-tuebingen-mut-alte-kulturen-9db4523d74/",
        "https://www.trauergruppe.de/tuebingen/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/1.html/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/100.html/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/2.html/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/3.html/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/4.html/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/5.html/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-airport-frankfurt-area-1005-5939/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-bad-soden-1005-13855/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-baden-baden-downtown-area-1005-6092/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-bockenheim-1005-1637/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-bonn-city-center-1005-6010/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-downtown-of-fussen-1005-14605/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-frankfurt-city-centre-1005-1633/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-frankfurt-hauptbahnhof-1005-13850/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-gallus-1005-12031/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-hauptbahnhof-1005-6037/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-hochst-1005-1642/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-interlaken-city-center-1005-8064/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-karlsruhe-city-center-1005-11754/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-munich-airport-area-1005-6040/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-neighborhood-1005-14611/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-neighborhood-1005-14613/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-niederrad-1005-1638/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-nordend-1005-5945/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-nymphenburg-palace-1005-13868/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-obermenzing-1005-6042/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-obersendling-1005-6043/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-offenbacham-main-1005-5944/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-ostend-1005-1635/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-perlach-1005-11510/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-sachsenhausen-1005-1641/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-strasbourg-downtown-1005-6479/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-stuttgart-mitte-1005-1511/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-thalkirchen-1005-6046/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-westend-1005-1636/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/business-district-wurzburg-city-center-1005-5830/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/comment-count-1011-10/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/comment-count-1011-100/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/comment-count-1011-50/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/comment-score-48-4.0/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/comment-score-48-4.5/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/ticket-book-available-today-42-true/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/ticket-book-available-tomorrow-43-true/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/ticket-book-free-entry-60-true/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-architecture-and-landmarks-70-131/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-exhibition-centers-70-129/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-historic-sites-70-132/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-lifestyle-70-165/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-nature-70-160/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-outdoor-sports-70-141/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-parks-70-133/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-religious-sites-70-145/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-sightseeing-tours-70-128/",
        "https://www.trip.com/travel-guide/attraction/tubingen-44519/tourist-attractions/type-all-of-traditional-cultural-experiences-70-130/",
        "https://www.trip.com/travel-guide/attraction/tubingen/homentubingen-96721/",
        "https://www.trommelschule-tuebingen.de/",
        "https://www.trz-tuebingen.de/",
        "https://www.tsg-tuebingen.de/",
        "https://www.tsg-tuebingen.de/abteilungen/",
        "https://www.tsg-tuebingen.de/abteilungen/badminton/",
        "https://www.tsg-tuebingen.de/abteilungen/breitensport/",
        "https://www.tsg-tuebingen.de/abteilungen/breitensport/trainingszeiten/",
        "https://www.tsg-tuebingen.de/abteilungen/fussball/",
        "https://www.tsg-tuebingen.de/abteilungen/handball/",
        "https://www.tsg-tuebingen.de/abteilungen/kunstturnen/",
        "https://www.tsg-tuebingen.de/abteilungen/lacrosse/",
        "https://www.tsg-tuebingen.de/abteilungen/leichtathletik/",
        "https://www.tsg-tuebingen.de/abteilungen/rhythmische-sportgymnastik/",
        "https://www.tsg-tuebingen.de/abteilungen/tennis/",
        "https://www.tsg-tuebingen.de/abteilungen/versehrtensport/",
        "https://www.tsg-tuebingen.de/abteilungen/volleyball/",
        "https://www.tsg-tuebingen.de/abteilungen/volleyball/trainingszeiten/",
        "https://www.tsg-tuebingen.de/aktuelle-angebote/bewegte-pause/",
        "https://www.tsg-tuebingen.de/aktuelle-angebote/bgf/",
        "https://www.tsg-tuebingen.de/cross-sport-fuer-jugendliche/",
        "https://www.tsg-tuebingen.de/cross-sport-fuer-jugendliche/kursuebersicht/",
        "https://www.tsg-tuebingen.de/datenschutz/",
        "https://www.tsg-tuebingen.de/downloads/",
        "https://www.tsg-tuebingen.de/feriencamps/",
        "https://www.tsg-tuebingen.de/feriencamps/termine/",
        "https://www.tsg-tuebingen.de/files/7914/5692/0793/Anwesenheitsliste_Kurse_blanko.xlsx/",
        "https://www.tsg-tuebingen.de/gesundheitssport/",
        "https://www.tsg-tuebingen.de/gesundheitssport/bgf/kontakt/",
        "https://www.tsg-tuebingen.de/gesundheitssport/kursuebersicht/",
        "https://www.tsg-tuebingen.de/gesundheitssport/kursuebersicht/bewegt-fit-rundum/",
        "https://www.tsg-tuebingen.de/gesundheitssport/kursuebersicht/hatha-yoga/",
        "https://www.tsg-tuebingen.de/gesundheitssport/kursuebersicht/pilates/",
        "https://www.tsg-tuebingen.de/gesundheitssport/kursuebersicht/zumba/",
        "https://www.tsg-tuebingen.de/gesundheitssport/reha-kurse/kontakt/",
        "https://www.tsg-tuebingen.de/kindergeburtstage/",
        "https://www.tsg-tuebingen.de/kindergeburtstage/kontakt/",
        "https://www.tsg-tuebingen.de/kindergeburtstage/termine/",
        "https://www.tsg-tuebingen.de/kiss-kindersportschule/",
        "https://www.tsg-tuebingen.de/kletteranlage/",
        "https://www.tsg-tuebingen.de/kletteranlage/kletterangebote/",
        "https://www.tsg-tuebingen.de/kontakt-anmeldung/",
        "https://www.tsg-tuebingen.de/kontakt-anmeldung/beitraege/",
        "https://www.tsg-tuebingen.de/kontakt-anmeldung/downloads-ul/",
        "https://www.tsg-tuebingen.de/sport-abc1/",
        "https://www.tsg-tuebingen.de/sportanlage/",
        "https://www.tsg-tuebingen.de/sportzentrum1/",
        "https://www.tsg-tuebingen.de/sportzentrum1/ausstattung/",
        "https://www.tsg-tuebingen.de/sportzentrum1/offene-stunden/",
        "https://www.tsg-tuebingen.de/sportzentrum1/preise/",
        "https://www.tsg-tuebingen.de/tsg-kindersportschule/",
        "https://www.tsg-tuebingen.de/tsg-kindersportschule/gebuehren/",
        "https://www.tsg-tuebingen.de/tsg-kindersportschule/kontakt/",
        "https://www.tsg-tuebingen.de/tsg-kindersportschule/kursuebersicht/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/datenschutz/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/familiensporttag/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/fsj/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/satzung/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/sportgala/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/stellenangebote/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/tsg-abc/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/tsg-newsletter/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/tsg-stammtisch/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/vereinskollektion/",
        "https://www.tsg-tuebingen.de/verein-tsg-abc/vorstand/",
        "https://www.tsg-tuebingen.de/verein/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/ausruestung/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/events/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/galerie/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/historie/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/kontakt/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/news/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/schiedsrichter_innen/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/1-mannschaft/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/2-mannschaft/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/b-juniorinnen-u17/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/c-juniorinnen-u15/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/d-juniorinnen-ii-u13/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/d-juniorinnen-u13/",
        "https://www.tsv-lustnau.de/frauenfussball-tuebingen/teams/frauenfussball-team-frauen-3/",
        "https://www.tsv-lustnau.de/niederlage-damen-1-im-derby-gegen-tc-tuebingen/",
        "https://www.ttc-tuebingen.de/",
        "https://www.ttc-tuebingen.de/datenschutzhinweise.html",
        "https://www.ttc-tuebingen.de/der-verein/das-trz/",
        "https://www.tuebingen-annarbor.de/",
        "https://www.tuebingen-annarbor.de/site.php/",
        "https://www.tuebingen-hohenheim.de/",
        "https://www.tuebingen-info.de/",
        "https://www.tuebingen-info.de/0/uebernachten/appartements-tuebingen.html",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/gastronomie/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/stadtfuehrungen/oeffentliche-themenfuehrungen/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/stadtfuehrungen/stadtfuehrungen-fuer-gruppen/themenfuehrungen/das-franzoesische-viertel/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/stadtfuehrungen/stadtfuehrungen-fuer-gruppen/themenfuehrungen/gogen-und-gelehrte-fuehrung-im-historischen-gewand/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/stadtfuehrungen/stadtfuehrungen-fuer-gruppen/themenfuehrungen/quacksalber-wundaerzte-und-chirurgen/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/stadtfuehrungen/stadtfuehrungen-fuer-gruppen/themenfuehrungen/tuebinger-universitaetsgeschichte-n/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/tuebingen-fuer/tagungs-und-kongressteilnehmer/conference-ticket/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/uebernachten-arrangements/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/uebernachten-arrangements/uebernachtungsarrangements/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/uebernachten-arrangements/uebernachtungsarrangements/tuebinger-melange/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/uebernachten/",
        "https://www.tuebingen-info.de/de/mein-aufenthalt/uebernachten/uebernachtungsarrangements/tuebingen-hole-in-one/",
        "https://www.tuebingen-info.de/de/service/presse-fotos/",
        "https://www.tuebingen-info.de/de/service/presse-fotos/pressefotos/",
        "https://www.tuebingen-info.de/de/service/vor-ort/zu-fuss/",
        "https://www.tuebingen-info.de/de/tuebinger-flair/kultur-veranstaltungen-tickets/",
        "https://www.tuebingen-info.de/de/urlaub/",
        "https://www.tuebingen-info.de/de/veranstaltungen#/event/",
        "https://www.tuebingen-info.de/de/veranstaltungen#/eventDate/1da1eb04-7dbb-41bd-b9e2-f6b5f57d37d7/",
        "https://www.tuebingen-info.de/de/veranstaltungen#/eventDate/47e17cd6-e2a8-4d6e-adab-68fef4b9d668/",
        "https://www.tuebingen-info.de/de/veranstaltungen#/eventDate/8d02b4b3-0523-4377-a68b-10c76f4ed80b/",
        "https://www.tuebingen-info.de/tuebingen/event/detail/Afrikafestival-Tuebingen-433820/",
        "https://www.tuebingen-info.de/tuebingen/ukv/house/ibis-styles-Tuebingen-FIT00020070492880268/",
        "https://www.tuebingen-info.de/tuebinger-blaetter.html",
        "https://www.tuebingen-info.de/uebernachten/privatzimmer-in-tuebingen.html",
        "https://www.tuebingen-kultur.reservix.de/",
        "https://www.tuebingen-macht-blau.de/",
        "https://www.tuebingen-macht-blau.de/energiekarawane/",
        "https://www.tuebingen-macht-blau.de/gasgespart/",
        "https://www.tuebingen-macht-blau.de/haus.energie.zukunft/",
        "https://www.tuebingen-macht-schlau.de/",
        "https://www.tuebingen-university-press.de/",
        "https://www.tuebingen-wit.de/",
        "https://www.tuebingen.de/",
        "https://www.tuebingen.de/ /",
        "https://www.tuebingen.de/148.html#/340/3436kita198/",
        "https://www.tuebingen.de/1520.html#/1952/",
        "https://www.tuebingen.de/1520.html#/1991/",
        "https://www.tuebingen.de/1620.html#/26103/",
        "https://www.tuebingen.de/1620.html#/34094/",
        "https://www.tuebingen.de/2117.html#/1015/",
        "https://www.tuebingen.de/2117.html#/25505/26284/",
        "https://www.tuebingen.de/23407.html#/19543/",
        "https://www.tuebingen.de/23416.html#/1038/",
        "https://www.tuebingen.de/23418.html#/23444/",
        "https://www.tuebingen.de/23419.html#/26441/",
        "https://www.tuebingen.de/29.html#/673/",
        "https://www.tuebingen.de/3393.html#/15307/",
        "https://www.tuebingen.de/75.html",
        "https://www.tuebingen.de/buergerapp/",
        "https://www.tuebingen.de/corona-notbetreuung#/28622/",
        "https://www.tuebingen.de/einkaufsfuehrer/default/show/id/6735/",
        "https://www.tuebingen.de/en/",
        "https://www.tuebingen.de/europaplatz/",
        "https://www.tuebingen.de/fairtrade/",
        "https://www.tuebingen.de/familienbeauftragte/",
        "https://www.tuebingen.de/feuerwehr/",
        "https://www.tuebingen.de/formularverwaltung/barrierefreiheit/",
        "https://www.tuebingen.de/hesse/",
        "https://www.tuebingen.de/impressum.html",
        "https://www.tuebingen.de/jugendbuchwoche/",
        "https://www.tuebingen.de/kreisbonuscard/",
        "https://www.tuebingen.de/kultur/",
        "https://www.tuebingen.de/leichte_sprache/",
        "https://www.tuebingen.de/literaturpfad/",
        "https://www.tuebingen.de/mobil/stadtplan/parkhaeuser/",
        "https://www.tuebingen.de/musikschule/",
        "https://www.tuebingen.de/pressemitteilungen/1620/34094.html",
        "https://www.tuebingen.de/regional-stadtbahn/",
        "https://www.tuebingen.de/regionalstadtbahn/",
        "https://www.tuebingen.de/spas/",
        "https://www.tuebingen.de/stadtbuecherei/",
        "https://www.tuebingen.de/stadtbuecherei/1310.html",
        "https://www.tuebingen.de/stadtmuseum/",
        "https://www.tuebingen.de/stadtmuseum/16899.html#/26256/",
        "https://www.tuebingen.de/stadtplan/",
        "https://www.tuebingen.de/streik/",
        "https://www.tuebingen.de/testmobile/",
        "https://www.tuebingen.de/tuebingen-macht-blau/klimatag/",
        "https://www.tuebingen.de/tuebingen-macht-blau/sterne-betriebe/",
        "https://www.tuebingen.de/verpackungssteuer/",
        "https://www.tuebingen.de/verwaltung/dienststellen#gleichstellung_integration/",
        "https://www.tuebingen.de/verwaltung/dienststellen#kommunale_servicebetriebe_tuebingen_kst/",
        "https://www.tuebingen.de/verwaltung/dienststellen#kultur/",
        "https://www.tuebingen.de/verwaltung/dienststellen#kunst_kultur/",
        "https://www.tuebingen.de/verwaltung/dienststellen#sozialhilfe/",
        "https://www.tuebingen.de/verwaltung/dienststellen#stadtentwaesserung/",
        "https://www.tuebingen.de/verwaltung/dienststellen#wasserwirtschaft/",
        "https://www.tuebingen.de/verwaltung/dienststellen/stadtentwaesserung/",
        "https://www.tuebingen.de/verwaltung/verfahren#/W/wohnberechtigungsschein/",
        "https://www.tuebingen.de/verwaltung/verfahren#anmietung_von_raeumen_im_salzstadel/",
        "https://www.tuebingen.de/verwaltung/verfahren#bonuscard/",
        "https://www.tuebingen.de/verwaltung/verfahren#kindercard/",
        "https://www.tuebingen.de/wahl/app/wahlraum.html",
        "https://www.tuebingen.de/wahlen/",
        "https://www.tuebingen.de/zob-quiz/",
        "https://www.tuebingen.ferienprogramm-online.de/",
        "https://www.tuebingen.greenpeace.de/",
        "https://www.tuebingen.mpg.de/188036/bibliothek/",
        "https://www.tuebingen.mpg.de/188109/bibliothek/",
        "https://www.tuebingen.mpg.de/en/jobs-career/jobs-career/",
        "https://www.tuebingen.mpg.de/karriere/current-jobs/",
        "https://www.tuebingen.mpg.de/nc/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/dzd/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/dzne/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/fml/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/hih/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/iwm/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/mpieb/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/mpiis/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/mpikyb/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/nmi/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/ukt/",
        "https://www.tuebingenresearchcampus.com/campus/partner-institutions/university-of-tuebingen/",
        "https://www.tuebingenresearchcampus.com/research-in-tuebingen/tnc/",
        "https://www.tuedilab-tuebingen.de/",
        "https://www.tuedilb-tuebingen.de/",
        "https://www.tuefa-tuebingen.de/",
        "https://www.tuefa-tuebingen.de/hilfsangebote/efa/",
        "https://www.tuemarkt.de/firma/Anja_Tressel_uomo_donna-tuebingen-15.html",
        "https://www.tuemarkt.de/firma/Baeckerei_Gehr_im_Nonnenhaus-tuebingen-20491.html",
        "https://www.tuemarkt.de/firma/Betten_Hottmann-tuebingen-227.html",
        "https://www.tuemarkt.de/firma/dreiraum__-_Galerie_fuer_Mode_und_Accessoires-tuebingen-41838.html",
        "https://www.tuemarkt.de/firma/Fauser_Kacheloefen_und_Kamine-tuebingen-646.html",
        "https://www.tuemarkt.de/firma/Gruengold_Meistergoldschmiede-tuebingen-36371.html",
        "https://www.tuemarkt.de/firma/Marbello-tuebingen-933.html",
        "https://www.tuemarkt.de/firma/Modehaus_Zinser-tuebingen-604.html",
        "https://www.tuemarkt.de/firma/MOKKA-tuebingen-348.html",
        "https://www.tuemarkt.de/firma/Olivle-tuebingen-347.html",
        "https://www.tuemarkt.de/firma/Optik_Maisch-tuebingen-100.html",
        "https://www.tuemarkt.de/firma/Silberburg_am_Markt-tuebingen-503.html",
        "https://www.tuemarkt.de/firma/Strebel-Hiltwein_Optik_GmbH-tuebingen-634.html",
        "https://www.tuemarkt.de/firma/style_afFAIRe-tuebingen-36373.html",
        "https://www.tuemarkt.de/firma/Villa_Willi-tuebingen-1035.html",
        "https://www.tuemarkt.de/firma/Vivendi_-_Mode_fuer_Frauen-tuebingen-608.html",
        "https://www.tuemarkt.de/firma/Wenke_Kunst-tuebingen-616.html",
        "https://www.tuemarkt.de/firma/wohnzimmer_am_park-tuebingen-41463.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/104/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/106/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/108/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/110/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/36/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/38/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/40/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/42/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/46/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/48/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/56/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/72/",
        "https://www.tuemarkt.de/tuebingen-erleben-2020/84/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2022/76/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/100-101/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/34-35/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/40-41/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/44-45/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/46-47/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/54-55/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/70-71/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/82-83/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/90-91/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/92-93/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/94-95/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/98-99/index.html",
        "https://www.tuemarkt.de/tuebingen-erleben-2023/index.html",
        "https://www.tueshop.de/product-category/geschaefte-tuebingen/baeckerei-gehr/",
        "https://www.tueshop.de/product-category/geschaefte-tuebingen/biwakschachtel/",
        "https://www.tueshop.de/product-category/geschaefte-tuebingen/brodbeck-leuchten/",
        "https://www.tueshop.de/product-category/geschaefte-tuebingen/contigo/",
        "https://www.tueshop.de/product-category/geschaefte-tuebingen/strebel-hiltwein/",
        "https://www.turbo-turtles-tuebingen.de/",
        "https://www.twitter.com/thwtuebingen/",
        "https://www.ub.uni-tuebingen.de/",
        "https://www.udo-tuebingen.de/",
        "https://www.udo-tuebingen.de/karriere/ausbildung/",
        "https://www.umweltzentrum-tuebingen.de/",
        "https://www.uni-frauenklinik-tuebingen.de/",
        "https://www.uni-tuebingen.de/",
        "https://www.uni-tuebingen.de/aktuelles/kontakt.html",
        "https://www.uni-tuebingen.de/aktuelles/newsletter-uni-tuebingen-aktuell/2017/2/index.html",
        "https://www.uni-tuebingen.de/aktuelles/veranstaltungskalender.html",
        "https://www.uni-tuebingen.de/collegium/",
        "https://www.uni-tuebingen.de/de/10/",
        "https://www.uni-tuebingen.de/de/1139/",
        "https://www.uni-tuebingen.de/de/119517/",
        "https://www.uni-tuebingen.de/de/2231/",
        "https://www.uni-tuebingen.de/de/333/",
        "https://www.uni-tuebingen.de/de/384/",
        "https://www.uni-tuebingen.de/de/385/",
        "https://www.uni-tuebingen.de/de/389/",
        "https://www.uni-tuebingen.de/de/39634/",
        "https://www.uni-tuebingen.de/de/457/",
        "https://www.uni-tuebingen.de/de/48773/",
        "https://www.uni-tuebingen.de/de/50350/",
        "https://www.uni-tuebingen.de/de/53565/",
        "https://www.uni-tuebingen.de/de/59313/",
        "https://www.uni-tuebingen.de/de/64/",
        "https://www.uni-tuebingen.de/de/78208/",
        "https://www.uni-tuebingen.de/de/81749/",
        "https://www.uni-tuebingen.de/einrichtungen/informations-kommunikations-und-medienzentrum-ikm/e-learning-portal-elp/lernplattformen.html",
        "https://www.uni-tuebingen.de/einrichtungen/personalvertretungen-beratungsdienste-und-beauftragte/lageplaene.html",
        "https://www.uni-tuebingen.de/einrichtungen/personalvertretungen-beratungsdienste-und-beauftragte/lageplaene/behindertengerechte-aufgaenge.html",
        "https://www.uni-tuebingen.de/einrichtungen/service/lageplaene/karte-b-wilhelmstrasse-talkliniken/alte-botanik.html",
        "https://www.uni-tuebingen.de/einrichtungen/stabsstellen/hochschulkommunikation/tagungs-und-praesentationsmaterial.html",
        "https://www.uni-tuebingen.de/einrichtungen/verwaltung-dezernate/ii-studium-und-lehre/tuebinger-zentrum-fuer-wissenschaftliche-weiterbildung.html",
        "https://www.uni-tuebingen.de/einrichtungen/verwaltung-dezernate/ii-studium-und-lehre/tuebinger-zentrum-fuer-wissenschaftliche-weiterbildung/",
        "https://www.uni-tuebingen.de/einrichtungen/verwaltung-dezernate/ii-studium-und-lehre/zentrale-studienberatung-zsb.html",
        "https://www.uni-tuebingen.de/einrichtungen/verwaltung-dezernate/iii-internationale-angelegenheiten/fachsprachenzentrum/fachsprachenzentrum.html",
        "https://www.uni-tuebingen.de/einrichtungen/verwaltung-dezernate/vi-bau-sicherheit-und-umwelt/abteilung-3/emas-prozess-an-der-universitaet.html",
        "https://www.uni-tuebingen.de/einrichtungen/verwaltung/iv-studierende/studierendenabteilung/statistiken.html",
        "https://www.uni-tuebingen.de/en.html",
        "https://www.uni-tuebingen.de/en/",
        "https://www.uni-tuebingen.de/en/10084/",
        "https://www.uni-tuebingen.de/en/10875/",
        "https://www.uni-tuebingen.de/en/11450/",
        "https://www.uni-tuebingen.de/en/12244/",
        "https://www.uni-tuebingen.de/en/13473/",
        "https://www.uni-tuebingen.de/en/16141/",
        "https://www.uni-tuebingen.de/en/17104/",
        "https://www.uni-tuebingen.de/en/26032/",
        "https://www.uni-tuebingen.de/en/31703/",
        "https://www.uni-tuebingen.de/en/35356/",
        "https://www.uni-tuebingen.de/en/36716/",
        "https://www.uni-tuebingen.de/en/39235/",
        "https://www.uni-tuebingen.de/en/42152/",
        "https://www.uni-tuebingen.de/en/4484/",
        "https://www.uni-tuebingen.de/en/46203/",
        "https://www.uni-tuebingen.de/en/48287/",
        "https://www.uni-tuebingen.de/en/483/",
        "https://www.uni-tuebingen.de/en/54849/",
        "https://www.uni-tuebingen.de/en/6354/",
        "https://www.uni-tuebingen.de/en/7335/",
        "https://www.uni-tuebingen.de/en/7403/",
        "https://www.uni-tuebingen.de/en/8013/",
        "https://www.uni-tuebingen.de/en/9255/",
        "https://www.uni-tuebingen.de/en/facilities/zentrale-einrichtungen/lisa.html",
        "https://www.uni-tuebingen.de/en/faculties/faculty-of-science/departments/computer-science/department.html",
        "https://www.uni-tuebingen.de/en/faculties/faculty-of-science/departments/geosciences/work-groups/urgeschichte-naturwissenschaftliche-archaeologie/forschungsbereich/institut-fuer-naturwissenschaftliche-archaeologie/arbeitsgruppe.html",
        "https://www.uni-tuebingen.de/en/university/job-advertisements/",
        "https://www.uni-tuebingen.de/en/university/news-and-publications.html",
        "https://www.uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/englisches-seminar.html",
        "https://www.uni-tuebingen.de/fakultaeten/zentrum-fuer-islamische-theologie/zentrum.html",
        "https://www.uni-tuebingen.de/footer/dritte-spalte/personensuche-epv.html",
        "https://www.uni-tuebingen.de/footer/dritte-spalte/timms-video-portal.html",
        "https://www.uni-tuebingen.de/footer/dritte-spalte/unishop.html",
        "https://www.uni-tuebingen.de/footer/erste-spalte/advice-for-international-students.html",
        "https://www.uni-tuebingen.de/footer/erste-spalte/campus-portal.html",
        "https://www.uni-tuebingen.de/footer/zweite-spalte/katalog-universitaetsbibliothek.html",
        "https://www.uni-tuebingen.de/footer/zweite-spalte/loginuni-tuebingen.html",
        "https://www.uni-tuebingen.de/footer/zweite-spalte/mensamenue.html",
        "https://www.uni-tuebingen.de/forschung/forschungsschwerpunkte.html",
        "https://www.uni-tuebingen.de/forschung/zentren-und-institute.html",
        "https://www.uni-tuebingen.de/gleichstellungsbeauftragte/",
        "https://www.uni-tuebingen.de/international/gastwissenschaftler/wohnen.html",
        "https://www.uni-tuebingen.de/kultur/",
        "https://www.uni-tuebingen.de/meta/datenschutzerklaerung/",
        "https://www.uni-tuebingen.de/meta/impressum/",
        "https://www.uni-tuebingen.de/nc/print/einrichtungen/universitaetsbibliothek/home.html",
        "https://www.uni-tuebingen.de/rss-de/457/",
        "https://www.uni-tuebingen.de/service/corporate-design/startseite.html",
        "https://www.uni-tuebingen.de/Studio-Literatur-Theater/",
        "https://www.uni-tuebingen.de/studium/studienangebot/studiengaenge-in-kooperation-mit-anderen-universitaeten.html",
        "https://www.uni-tuebingen.de/studium/studienorganisation/studentensekretariat.html",
        "https://www.uni-tuebingen.de/studium/verzeichnis-der-studiengaenge.html",
        "https://www.uni-tuebingen.de/universitaet/kulturelle-angebote/collegium-musicum.html",
        "https://www.uni-tuebingen.de/universitaet/profil/geschichte-der-universitaet.html",
        "https://www.uni-tuebingen.de/zielgruppen/beschaeftigte/service/downloadbereich.html",
        "https://www.unimuseum.uni-tuebingen.de/",
        "https://www.unimuseum.uni-tuebingen.de/de/museum-im-schloss.html",
        "https://www.unimuseum.uni-tuebingen.de/de/sammlungen.html",
        "https://www.unimuseum.uni-tuebingen.de/de/shop/",
        "https://www.unimuseum.uni-tuebingen.de/en/",
        "https://www.unimuseum.uni-tuebingen.de/museum-schloss/",
        "https://www.unimuseum.uni-tuebingen.de/sammlungen.html",
        "https://www.unterwegsunddaheim.de/2022/08/tuebingen-sehenswuerdigkeiten-in-der-universitaetsstadt-am-neckar/",
        "https://www.unterwegsunddaheim.de/2022/08/tuebingen-sehenswuerdigkeiten-in-der-universitaetsstadt-am-neckar/#comments/",
        "https://www.vba-tuebingen.de/",
        "https://www.vcd.org/tuebingen/",
        "https://www.vesperkirche-tuebingen.elk-wue.de/",
        "https://www.vfgss-tuebingen.de/",
        "https://www.vfgss-tuebingen.de/mensa/",
        "https://www.vfgss-tuebingen.de/mensa/ansprechpartner/",
        "https://www.vhs-tuebingen.de/",
        "https://www.vhs-tuebingen.de/kurssuche/kurs/Wie-lernen-Maschinen-und-was-ist-kuenstliche-Intelligenz/212-11001#inhalt/",
        "https://www.vhs-tuebingen.de/projekte/angebote-fuer-fluechtlinge-aus-der-ukraine/",
        "https://www.vhs-tuebingen.de/service/newsletter/",
        "https://www.vielfalt-kreis-tuebingen.de/,Lde/Startseite/foerderung/plenum.html",
        "https://www.vielfalt-kreis-tuebingen.de/Startseite.html",
        "https://www.viertelvortuebingen.de/",
        "https://www.villa-kunterbunt-tuebingen.de/",
        "https://www.vomfass.de/tuebingen/",
        "https://www.vr-tuebingen.de/",
        "https://www.vsp-net.de/tagesstruktur-und-arbeit/tagesstruktur-tuebingen/gaertnerei/",
        "https://www.waldorfkiga-tuebingen.de/",
        "https://www.waldorfkindergarten-tuebingen.de/",
        "https://www.walter-tools.com/de-de/company/mission_facts/production-units/Pages/pu-tuebingen.aspx",
        "https://www.wayfaringwithwagner.com/tag/tubingen/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10604/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10611/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10614/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10615/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10616/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10619/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10620/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10621/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10622/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10623/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10624/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10625/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10626/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10627/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10631/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10632/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10633/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10636/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10638/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10645/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10652/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10656/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10676/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10706/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comment-10724/",
        "https://www.wayfaringwithwagner.com/visiting-tuebingen-in-wintertime/#comments/",
        "https://www.we-celebrate.de/foodtruck-tuebingen/",
        "https://www.weinhaus-schmid-tuebingen.de/",
        "https://www.welcomecenter.uni-tuebingen.de/",
        "https://www.wgh-tuebingen.de/",
        "https://www.wila-tuebingen.de/",
        "https://www.wiso.uni-tuebingen.de/faecher/sportwissenschaft/studium/studiengaenge.html",
        "https://www.wissenschaftscampus-tuebingen.de/www/de/forschung/forschungsbereiche/projekt13/index.html",
        "https://www.wissenschaftscampus-tuebingen.de/www/en/index.html",
        "https://www.wsi.uni-tuebingen.de/",
        "https://www.wurzelkinder-tuebingen.de/",
        "https://www.zar.de/tuebingen/",
        "https://www.zdv.uni-tuebingen.de/zustandsansicht.html",
        "https://www.zeit.de/2018/38/cyber-valley-kuenstliche-intelligenz-zentrum-tuebingen/seite-2/",
        "https://www.zeit.de/politik/deutschland/2022-10/ob-wahl-tuebingen-boris-palmer/",
        "https://www.zimmertheater-tuebingen.de/",
        "https://www.zimmertheater-tuebingen.de/itz/66/irrlichter-ein-sommernachtstrauma/",
        "https://www.zum-alten-fritz-tuebingen.de/",
        "https://www.zwergenreich-tuebingen.de/",
        "https://www2.medizin.uni-tuebingen.de/publicETB/servlet/eGuide/",
        "https://wwwopac.komm.one/daituebingen/",
        "https://zeig-mir-tuebingen.de/silberburg/",
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
