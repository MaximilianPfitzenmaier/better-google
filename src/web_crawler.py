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
from rake_nltk import Rake
from datetime import datetime
import threading
from translate import Translator

# Create a thread-local instance of WordNet and a lock
wordnet_lock = threading.Lock()
db_lock = threading.Lock()
translation_lock = threading.Lock()
kw_model = keybert.KeyBERT()
# Define a thread subclass for crawling URLs


class CrawlThread(threading.Thread):
    def __init__(self, crawler, url):
        super().__init__()
        self.crawler = crawler
        self.url = url

    def run(self):
        self.crawler.crawl_url(self.url)


class Crawler:
    initial_frontier = [
        'https://hoelderlinturm.de/english/',
        # reichen solche datenbanken?

        'https://civis.eu/en/about-civis/universities/eberhard-karls-universitat-tubingen/',
        'https://tuebingenresearchcampus.com/',
        'https://is.mpg.de/',
        # noch mehr guides, decken aber gut ab - zumal eh die einzelnen seiten idr nur auf deutsch sind
        'https://www.tripadvisor.com/Attractions-g198539-Activities-Tubingen_Baden_Wurttemberg.html',
        'https://www.medizin.uni-tuebingen.de/en-de/startseite/',
        'https://apps.allianzworldwidecare.com/poi/hospital-doctor-and-health-practitioner-finder?PROVTYPE=PRACTITIONERS&TRANS=Doctors%20and%20Health%20Practitioners%20in%20Tuebingen,%20Germany&CON=Europe&COUNTRY=Germany&CITY=Tuebingen&choice=en/',
        'https://www.yelp.com/search?cflt=physicians&find_loc=Tübingen%2C+Baden-W%C3%BCrttemberg%2C+Germany/',
        'https://cyber-valley.de/',
        'https://www.tuebingen.mpg.de/84547/cyber-valley/',
        'https://tuebingen.ai/',
        'https://www.eml-unitue.de/',
        'https://en.wikipedia.org/wiki/Tübingen/',
        'https://wikitravel.org/en/Tübingen/',
        'https://www.bahnhof.de/en/tuebingen-hbf/',
        # politics
        # geograpy
        'https://www.engelvoelkers.com/en-de/properties/rent-apartment/baden-wurttemberg/tubingen-kreis/',
        'https://integreat.app/tuebingen/en/news/tu-news/',
        'https://tunewsinternational.com/category/news-in-english/',

        # top 100 tuebingen
        'https://www.tuebingen.de/',
        'https://www.unterwegsunddaheim.de/2022/08/tuebingen-sehenswuerdigkeiten-in-der-universitaetsstadt-am-neckar/#:~:text=Tübingen%20ist%20eine%20der,h%C3%BCbsche%20Altstadt%20direkt%20am%20Neckarufer./',
        'https://uni-tuebingen.de/fakultaeten/philosophische-fakultaet/fachbereiche/neuphilologie/seminar-fuer-sprachwissenschaft/studium-lehre/studiengaenge/faq/warum-in-tuebingen-studieren/#:~:text=Die%20ber%C3%BChmte%20Altstadt%20mit%20ihren,nie%20%22zu%20ruhig%22%20wird./',
        'https://www.tripadvisor.de/Attractions-g198539-Activities-Tubingen_Baden_Wurttemberg.html',
        'https://www.kreis-tuebingen.de/314579.html#:~:text=Neben%20der%20Schw%C3%A4bischen%20Alb%20und,die%20T%C3%BCbinger%20Bucht%20wie%20heute./',
        'https://www.tuebingen-info.de/',
        'https://de.wikipedia.org/wiki/Tuebingen/',
        'https://uni-tuebingen.de/',
        'https://www.kreis-tuebingen.de/Startseite.html',
        'https://rp.baden-wuerttemberg.de/rpt/',
        'https://kunsthalle-tuebingen.de/',
        'https://uni-tuebingen.de/universitaet/',
        'https://www.facebook.com/tuebingen.de/',
        'https://www.tripadvisor.de/Tourism-g198539-Tubingen_Baden_Wurttemberg-Vacations.html',
        'https://www.stern.de/politik/deutschland/themen/tuebingen-4161038.html',
        'https://www.germany.travel/de/staedte-kultur/tuebingen.html',
        'https://www.institutfrancais.de/tuebingen/',
        'https://www.landestheater-tuebingen.de/',
        'https://www.tagblatt.de/',
        'https://www.ksk-tuebingen.de/de/home.html',
        'https://www.swtue.de/index.html',
        'https://www.dai-tuebingen.de/',
        'https://staatsanwaltschaft-tuebingen.justiz-bw.de/pb/,Lde/Startseite/',
        'https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/index.html',
        'https://www.sueddeutsche.de/thema/Tübingen/',
        'https://www.tsg-tuebingen.de/',
        'https://www.gea.de/neckar-alb/kreis-tuebingen.html',
        'https://www.tuemarkt.de/',
        'https://www.youtube.com/channel/UCw8ZjcyEoZHEMnJYN_DuO6A/',
        'https://www.dzif.de/de/standorte/tuebingen/',
        'https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/index.html',
        'https://www.tsg-tuebingen.de/',
        'https://de.wikivoyage.org/wiki/Tübingen/',
        'https://www.gea.de/neckar-alb/kreis-tuebingen.html',
        'https://www.tuemarkt.de/',
        'https://www.youtube.com/channel/UCw8ZjcyEoZHEMnJYN_DuO6A/',
        'https://www.dzif.de/de/standorte/tuebingen/',
        'https://www.lebenshilfe-tuebingen.de/',
        'https://www.tif-tuebingen.de/',
        'https://www.dav-tuebingen.de/',
        'https://viel-unterwegs.de/reiseziele/deutschland/baden-wuerttemberg/tuebingen-sehenswuerdigkeiten/',
        'http://www.wila-tuebingen.de/',
        'https://www.cvjm-tuebingen.de/',
        'https://www.zdf.de/politik/laenderspiegel/unterwegs-in-tuebingen-100.html',
        'https://tigers-tuebingen.de/',
        'https://www.zimmertheater-tuebingen.de/',
        'https://www.museumsgesellschaft-tuebingen.de/',
        'https://www.vermoegenundbau-bw.de/ueber-uns/standorte/amt-tuebingen/',
        'https://www.bg-kliniken.de/klinik-tuebingen/',
        'https://www.altenhilfe-tuebingen.de/',
        'https://tue.schulamt-bw.de/Startseite/',
        'http://www.ssc-tuebingen.de/',
        'https://www.nabu-tuebingen.de/',
        'https://jgr-tuebingen.de/',
        'https://www.boxenstop-tuebingen.de/',
        'https://naturfreunde-tuebingen.de/',
        'https://www.lpb-tuebingen.de/',
        'https://ov-tuebingen.thw.de/',
        'https://www.mein-check-in.de/tuebingen/overview/',
        'https://wilhelmsstift.de/',
        'https://www.hochschulregion.de/',
        'https://www.krone-tuebingen.de/de/',
        'https://www.profamilia.de/angebote-vor-ort/baden-wuerttemberg/tuebingen/',
        'https://kreisbau.com/',
        'https://sommernachtskino.de/',
        'https://www.my-stuwe.de/',
        'https://www.gss-tuebingen.de/',
        'https://www.evangelische-gesamtkirchengemeinde-tuebingen.de/',
        'https://www.drk-tuebingen.de/',
        'https://sv03-tuebingen.de/',
        'https://www.mey-generalbau-triathlon.com/',
        'https://www.kulturnetz-tuebingen.de/',
        'https://umweltzentrum-tuebingen.de/',
        'https://www.gwg-tuebingen.de/',
        'https://www.faz.net/aktuell/feuilleton/thema/tuebingen/',
        'https://uro-tuebingen.de/',
        'https://mrw-tuebingen.de/',
        'https://www.hih-tuebingen.de/',
        'https://www.neckarcamping.de/',
        'https://www.vhs-tuebingen.de/',
        'https://www.kirchenmusikhochschule.de/',
        'https://katholisch-tue.de/',
        'https://tuebingen.ai/',
        'https://geburtshaus-tuebingen.de/',
        'https://www.sudhaus-tuebingen.de/',
        'https://www.hospiz-tuebingen.de/',
        'https://www.hgv-tuebingen.de/',
        'https://www.stura-tuebingen.de/',
        'https://www.jacques.de/depot/44/tuebingen/',
        'https://www.stiftskirche-tuebingen.de/',
        'https://www.stadtseniorenrat-tuebingen.de/',
        'https://www.antiquitaeten-tuebingen.de/',
        'https://www.blutspendezentrale.de/',
        'https://www.osiander.de/buchhandlung/5290/',
        'https://www.raktuebingen.de/',
        'https://www.abfall-kreis-tuebingen.de/',
        'https://www.tierschutzverein-tuebingen.de/',
        'https://www.evstift.de/',
        'https://www.sozialforum-tuebingen.de/',
        'http://www.tageselternverein.de/',
        'https://www.arbeitsagentur.de/vor-ort/reutlingen/tuebingen/',
        'https://finanzamt-bw.fv-bwl.de/fa_tuebingen/',
        'https://www.tuebingen.mpg.de/nc/',
        'https://www.sit-sis.de/',
        'https://www.hornbach.de/mein-markt/baumarkt-hornbach-tuebingen/',
        'https://www.srg-tuebingen.de/',
        'https://elsa-tuebingen.de/',
        'https://tuebingen.dlrg.de/',
        'https://zsl-bw.de/,Lde/Startseite/ueber-das-zsl/regionalstelle-tuebingen/',
        'https://lebensphasenhaus.de/',
        'https://rds-tue.ibs-bw.de/opac/',
        'https://solawi-tuebingen.de/',
        'https://www.geschichtswerkstatt-tuebingen.de/',
        'https://www.sportkreis-tuebingen.de/',
        'https://www.agentur-fuer-klimaschutz.de/',
        'https://www.esg-tuebingen.de/',
        'https://www.biwakschachtel-tuebingen.de/',
        'https://www.feuerwehr-tuebingen.de/',
        'https://llpa.kultus-bw.de/,Lde/beim+Regierungspraesidium+Tuebingen/',
        'https://jobcenter-tuebingen.de/',
        'https://www.keb-tuebingen.de/',
        'https://www.gruene-tuebingen.de/home/',
        'https://www.meteoblue.com/de/wetter/woche/Tübingen_deutschland_2820860/',
        'https://nikolauslauf-tuebingen.de/start/',
        'https://sowit.de/',
        'https://www.wetteronline.de/wetter/tuebingen/',
        'https://www.wetter.com/deutschland/tuebingen/DE0010334.html',
        'https://www.wetter.com/wetter_aktuell/wettervorhersage/morgen/deutschland/tuebingen/DE0010334.html',
        'https://nachrichten.idw-online.de/2023/07/18/nationales-forschungszentrum-fuer-ki-spitzenforschung-in-tuebingen-feiert-seine-gruendung/',
        'https://www.baunetz.de/meldungen/Meldungen-Gewerbebau_von_rundzwei_Architekten_bei_Tuebingen_8267073.html',
        'https://www.deutschlandfunk.de/ki-zentrum-tuebingen-wird-eingeweiht-cyber-valley-dlf-dcb022f3-100.html',
        'https://www.dasding.de/newszone/tuebingen-schule-auszeit-ukraine-krieg-100.html',
        'https://www.sueddeutsche.de/wissen/wissenschaft-tuebingen-forschungszentrum-fuer-ki-spitzenforschung-gegruendet-dpa.urn-newsml-dpa-com-20090101-230718-99-446723/',
        'https://www.stuttgarter-wochenblatt.de/inhalt.original-ostermann-formel-1-rennen-in-tuebingen.e9ebad2a-747e-48f3-ad04-9e102f8fd8e1.html',
        'https://www.stuttgarter-zeitung.de/inhalt.ewald-frie-aus-tuebingen-vom-professor-zum-bestsellerautor.2e0c6208-ab09-4076-ae3b-1125129735cf.html',
        'https://www.radiobielefeld.de/nachrichten/lokalnachrichten/detailansicht/tuebingen-dieter-thomas-kuhn-kauft-brusthaartoupet-als-meterware.html',
        'https://www.stuttgarter-nachrichten.de/inhalt.ukrainer-in-tuebingen-drei-wochen-urlaub-vom-krieg.781d1bcf-28a3-4141-b380-43c5b6f40839.html',
        'https://versicherungswirtschaft-heute.de/schlaglicht/2023-07-14/lg-tubingen-trifft-richtungsweisendes-urteil-gegen-cyberversicherer/',
        'https://www.news.de/lokales/856482752/tuebingen-veranstaltungen-und-events-aktuell-im-juli-2023-konzert-comedy-freizeit-tipps-was-ist-am-wochenende-los/1/',

        # food
        'https://www.tripadvisor.de/Restaurants-g198539-Tubingen_Baden_Wurttemberg.html',
        'https://www.tripadvisor.de/Restaurants-g198539-zfp58-Tubingen_Baden_Wurttemberg.html',
        'https://www.lieferando.de/lieferservice/essen/tuebingen-72076/',
        'https://www.tuebingen.de/en/3504.html',
        'https://www.nuna-store.com/',
        'https://www.tuebingen-info.de/veranstaltungen/streetfood-fiesta-0bf84c9871/',
        'https://www.schummeltag-streetfood.de/event/street-food-festival-tuebingen-2021/',
        'https://www.burgermeister-cafegino.de/',
        'https://www.faros-tuebingen.com/',
        'https://www.slowfood.de/netzwerk/vor-ort/tuebingen/',
        'https://de.restaurantguru.com/fast-food-Tubingen-t11/',
        'https://www.restaurant-ranglisten.de/restaurants/ranglisten/deutschland/baden-wuerttemberg/tuebingen/kueche/slow-food/',
        'https://uni-tuebingen.de/pt/95901/',
        'https://www.abfall-kreis-tuebingen.de/entsorgen/verwerten/foodsharing/',
        'https://aris-kommt.de/',
        'https://www.slowfood.de/netzwerk/vor-ort/tuebingen/genussfuehrer/',
        'https://foodsharing.de/?page=fairteiler&bid=6/',
        'https://www.foodalley.de/stores/72070/Tuebingen/',
        'https://www.facebook.com/slowfoodtuebingen/',
        'https://www.thefork.com/restaurants/tubingen-c561333/',
        'https://wanderlog.com/list/geoCategory/199488/where-to-eat-best-restaurants-in-tubingen/',
        'https://guide.michelin.com/de/de/baden-wurttemberg/tbingen/restaurants/',
        'https://mph.tuebingen.mpg.de/en/menu/',
        'https://m.yelp.com/search?cflt=food&find_loc=Tübingen%2C+Baden-W%C3%BCrttemberg/',
        'https://www.diegutelaune.de/',
        'https://fierfood.eatbu.com/',
        'https://www.superfoodz-store.com/',
        'https://www.bongoroots.de/',
        'https://mezeakademie.com/',
        'https://tuebilicious.mewi-projekte.de/2021/06/06/supportyourlocals/',
        'https://mezeakademie.com/',
        'https://tuebilicious.mewi-projekte.de/2021/06/06/supportyourlocals/',
        'https://www.mehrrettich.de/',
        'https://genussart.club/food/',
        'https://www.we-celebrate.de/foodtruck-tuebingen/',
        'https://www.reddit.com/r/Tuebingen/comments/12ghnvz/best_place_to_grab_food_to_go/',
        'https://www.numbeo.com/food-prices/in/Tubingen/',
        'https://tuebingen.city-map.de/01100001/ofterdingen-steinlachtal/online-shops/food/',
        'https://yably.de/fast-food-restaurants/tuebingen/',
        'https://www.wurstkueche.com/en/frontpage-2/',
        'https://samphat-thai.de/',
        'https://www.foodtruckbooking.de/ort/72072-tubingen/',
        'https://food-festivals.com/suche/Tübingen/',
        'https://www.kupferblau.de/2020/12/18/die-besten-take-away-geheimtipps-in-tuebingen/',
        'https://lous-foodtruck.de/foodtruck-tuebingen-2/',
        'https://bueroaktiv-tuebingen.de/initiativen/praesentierensich/foodsharing-tuebingen/',
        'https://www.miomente.de/stuttgart/kulinarische-stadtfuehrung-tuebingen-meet-und-eat-tuebingen/',
        'https://www.die-food-trucks.de/nach-stadt/tubingen/',
        'https://www.happycow.net/europe/germany/tubingen/',
        'https://www.kohenoor-tuebingen.de/',
        'https://www.kaufda.de/Filialen/Tuebingen/Fast-Food/v-c24/',
        'https://branchenbuch.meinestadt.de/tuebingen/brazl/100-19055-19065-54919-78204/',
        'https://home.meinestadt.de/tuebingen/restaurant/',
        'https://www.dastelefonbuch.de/Branchen/Fast%20Food/Tübingen/',
        'https://www.my-stuwe.de/en/refectory/cafeteria-unibibliothek-tuebingen/',
        'https://www.eurofins.de/lebensmittel/labore/eurofins-food-testing-sued/eurofins-food-testing-sued/',
        'https://www.speicher-tuebingen.de/unser-bistro/',
        'https://www.gastroguide.de/city/tuebingen/schnell-mal-was-essen/',
        'https://www.infosperber.ch/wirtschaft/uebriges-wirtschaft/tuebingen-mcdonalds-muss-nun-doch-einweg-steuer-zahlen/',
        'https://www.sluurpy.de/Tübingen/restaurants/',
        'https://www.stepstone.de/jobs/food-%26-beverage/in-Tübingen/',
        'https://www.cositabonita.de/stores/Tübingen/',
        'https://umweltzentrum-tuebingen.de/wordpress/programm/',
        'https://fragdenstaat.de/anfrage/kontrollbericht-zu-asien-food-bazar-tubingen/',
        'https://www.sueddeutsche.de/wissen/verpackungssteuer-tuebingen-plastikmuell-1.5883210/',
        'https://foodwissen.de/kuechenstudio-tuebingen/',
        'https://www.meinprospekt.de/tuebingen/filialen/fast-food/',
        'https://www.littleindia-tuebingen.de/',
        'https://www.daznbarfinder.de/lokale/122652/ts-food-gmbh/',
        'https://www.northdata.de/TS+Food+GmbH,+Tübingen/Amtsgericht+Stuttgart+HRB+748766/',
        'https://www.experteer.de/jobs-Tübingen-nahrungsmittel-food-cid9801ind100/',
        'https://derproviantmeister.de/',
        'https://www.ibyteburgers.com/standorte-kalender/',
        'https://www.bverwg.de/pm/2023/40/',
        'https://www.bwegt.de/land-und-leute/das-land-erleben/veranstaltungen/detail/streetfood-festival-tuebingen/schummeltag-street-food-festival/37abfd6f-5ba4-407e-8274-e06f99b4cdc7/',
        'https://www.tagesschau.de/inland/tuebingen-verpackungssteuer-100.html',
        'https://www.food-service.de/maerkte/news/verpackungssteuer--tuebingen-steuer-auf-einweg-to-go-verpackungen-ist-rechtens-55986/',
        'https://unser-tuebingen.de/veranstaltung/street-food-festival-tuebingen-2023/',
        'https://ernaehrungsrat-tuebingen.de/',
        'https://firmeneintrag.creditreform.de/72072/7270059882/HORST_WIZEMANN_FIRE_FOOD_AND_ENTERTAINMENT/',
        'https://www.foodtruck-mieten24.de/food-truck-mieten-in-tuebingen/',
        'https://www.japengo.eu/',
        'https://allevents.in/tubingen/food-drinks/',
        'https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/foodsharing-cafe-lebensmittel-retten-100.html',
        'https://taz.de/Verpackungssteuer-in-Tuebingen/!5936857/',
        'https://www.germanfoodblogs.de/interviews/2019/6/12/jan-aus-tbingen-esszettel/',
        'https://bolt.eu/de-de/cities/tubingen/',
        'https://de.indeed.com/Food-Science-Jobs-in-Tübingen/',
        'https://www.schmaelzle.de/',
        'https://www.streetquizine.de/food-truck-catering/tubingen/',
        'https://www.erento.com/mieten/party_messe_events/gastronomie_bar/fun_food/tuebingen/',
        'https://nachbarskind.de/',
        'https://www.startnext.com/mehrrettich/',
        'https://www.vhs-tuebingen.de/kurse/gesundheit/kategorie/Essen+und+Trinken/288/',
        'https://www.neue-verpackung.de/food/verwaltungsgerichtshof-kippt-verpackungssteuer-in-tuebingen-225.html',
        'https://www.stilwild.de/',
        'https://meine-kunsthandwerker-termine.de/de/veranstaltung/street-food-festival-tuebingen_23109852/',
        'https://edeka-schoeck.de/filiale-tuebingen-berliner-ring/',
        'https://www.tuepedia.de/wiki/Hendl_Burg_(Bahnhof)/',
        'https://www.kleinanzeigen.de/s-anzeige/emergency-food/2474714274-87-9094/',
        'https://www.amigopizza-tuebingen.de/fast-food-lieferservice/',
        'https://www.sam-regional.de/de/magazinbeitraege-gastronomie/1/140/slow-food/',
        'https://freistil.beer/category/food-rebellen/',
        'https://feinschmeckerle.de/2018/05/12/food-rebellen-stilwild-tuebingen/',
        'https://www.11880.com/rueckwaertssuche/070719798106/',
        'https://www.companyhouse.de/TS-Food-GmbH-Tuebingen/',
        'https://tigers-tuebingen.de/tigers-tuebingen-kooperieren-mit-dem-berliner-performance-food-start-up/',
        'https://cafe-kunsthalle-tuebingen.com/',
        'https://www.spiegel.de/wirtschaft/service/tuebingen-plant-steuer-auf-fast-food-verpackungen-a-834b811e-1a28-4f4f-b8c3-ec4dd20659e2/',
        'https://www.tagblatt.de/Nachrichten/Tausende-Besucher-kamen-zum-ersten-Tuebinger-Street-Food-Markt-Gaumenfreude-290830.html',
        'https://crepes-tuebingen.de/events/kategorie/food-truck/list/?tribe_event_display=past&tribe_paged=1/',
        'http://dailyperfectmoment.blogspot.com/2014/03/friday-food-favourite-places-cafe.html',

        # sport
        'https://uni-tuebingen.de/einrichtungen/zentrale-einrichtungen/hochschulsport/home/',
        'https://uni-tuebingen.de/einrichtungen/zentrale-einrichtungen/hochschulsport/sportprogramm/',
        'https://www.tuebingen.de/577.html',
        'https://www.sfs-tuebingen.de/vereine/liste-der-sportarten/',
        'https://sv03-tuebingen.de/#:~:text=Das%20sportliche%20Angebot%20erstreckt%20sich,von%205%20%E2%80%93%2010%20Jahren%20bereichert./',
        'https://home.meinestadt.de/tuebingen/sport/',
        'https://www.tsg-tuebingen.de/',
        'https://www.easy-sports.com/tuebingen/',
        'https://www.instagram.com/hochschulsport_tuebingen/?hl=de/',
        'https://www.instagram.com/fachschaftsport_tuebingen/?hl=de/',
        'https://www.sportkreis-tuebingen.de/',
        'https://rp.baden-wuerttemberg.de/rpt/abt7/fachberater/seiten/sport/',
        'https://www.studieren-studium.com/studium/studieren/Sport-Tübingen/',
        'https://www.tagblatt.de/Nachrichten/Sport/',
        'https://www.intersport.de/haendlersuche/sportgeschaefte-baden-wuerttemberg/72072-tuebingen-intersport-raepple/',
        'https://sv03-tuebingen.de/',
        'https://www.post-sv-tuebingen.de/',
        'https://gym-tue.seminare-bw.de/,Lde/Startseite/Bereiche+_+Faecher/Sport/',
        'https://studiengaenge.zeit.de/studium/gesellschaftswissenschaften/sport/sport/standorte/baden-wuerttemberg/tuebingen/',
        'http://www.ssc-tuebingen.de/',
        'https://www.sport-studieren.de/hochschulen/universitaet-tuebingen/',
        'https://www.praeventionssport-tuebingen.de/',
        'https://www.gss-tuebingen.de/die-gss/gymnasium/fachbereiche/sport/',
        'https://www.dav-tuebingen.de/Bergsport/Nordic-Sport/Gruppen/',
        'https://www.studycheck.de/studium/sportwissenschaft/uni-tuebingen-20286/',
        'https://www.kreis-tuebingen.de/Startseite/landratsamt/sporthallen-+und+schulraumnutzung.html',
        'https://tigers-tuebingen.de/',
        'https://sportdeutschland.tv/tigers-tuebingen/',
        'https://www.studocu.com/de/course/eberhard-karls-universitat-tubingen/sport/2642045/',
        'https://www.tue-kiss.de/',
        'https://www.facebook.com/IfSTuebingen/?locale=de_DE/',
        'https://www.studis-online.de/studium/sport-sportwissenschaften/uni-tuebingen-23883/',
        'https://www.facebook.com/IfSTuebingen/?locale=de_DE/',
        'https://www.occ-tuebingen.de/orthopaedie/sportmedizin/',
        'https://www.habila.de/freizeit-teilhabe/fachstelle-inklusion-durch-sport/',
        'https://www.reservix.de/sport-in-tuebingen/',
        'https://www.dastelefonbuch.de/Branchen/Sport/Tübingen/',
        'https://studieren.de/sport-lehramt-uni-tuebingen.studiengang.t-0.a-68.c-408.html',
        'https://www.sportfechter.de/',
        'https://www.sport2000.de/stores/tuebingen/',
        'https://www.tuepedia.de/wiki/Kategorie:Sport/',
        'https://tue.schulamt-bw.de/,Lde/Startseite/Themen/Schulsport/',
        'https://www.ukt-physio.de/spezielle-therapie/sportphysiotherapie/',
        'https://www.medsports.de/',
        'https://sports-nut.de/',
        'https://tuebingen.wlv-sport.de/home/',
        'https://www.sportwelten.de/TSG-TUeBINGEN_1/',
        'https://www.hubnspoke.de/',
        'https://www.biwakschachtel-tuebingen.de/',
        'https://www.rskv-tuebingen.de/',
        'https://www.rrsct.de/',
        'https://sportraepple-shop.de/sportwissenschaft-tuebingen/',
        'https://www.eventbrite.de/b/germany--Tübingen/sports-and-fitness/',
        'https://urbansportsclub.com/de/venues/stuttgart/tuebingen-tuebingen/',
        'https://www.cvjm-tuebingen.de/angebote/sport-im-cvjm/',
        'https://www.rsg-tuebingen.de/',
        'https://www.swr.de/swraktuell/baden-wuerttemberg/tuebingen/weltkongress-sportsoziologie-tuebingen-100.html',
        'https://www.demografie-portal.de/DE/Politik/Baden-Wuerttemberg/Sport/interview-christine-vollmer-tuebingen.html',
        'https://www.bg-kliniken.de/klinik-tuebingen/fachbereiche/detail/sporttherapie/',
        'https://onlinestreet.de/271761-sportkreis-tuebingen-e-v-/',
        'https://www.vhs-tuebingen.de/',
        'https://hc-tuebingen.de/',
        'https://www.feuerwehr-tuebingen.de/ueber-uns/sport/',
        'https://www.ttc-tuebingen.de/',
        'https://nikolauslauf-tuebingen.de/start/',
        'https://tunewsinternational.com/2021/07/08/diesen-samstag-spas-sport-am-samstag-in-tubingen/',
        'https://mapet.de/',
        'https://www.swtue.de/unternehmen/verantwortung/gesellschaftliches-engagement/sponsoringanfrage-sport.html',
        'https://www.amos-reisen.de/reiseprogramm/tuebingen-und-ritter-sport/',
        'https://www.mcshape.com/studio/tuebingen/',
        'https://www.landestheater-tuebingen.de/Spielplan/Extras.html?id=27/',
        'https://karriere-im-sportmanagement.de/hochschulen/universitaet-tuebingen/',
        'https://www.nc-werte.info/hochschule/uni-tuebingen/sport-sportpublizistik/',
        'https://www.tsv-lustnau.de/',
        'https://www.tuebingen-info.de/veranstaltungen/spas-sport-am-samstag-plus-472c93c6d7/',
        'https://de.indeed.com/q-sport-l-Tübingen-jobs.html',
        'https://xn--yogaloft-tbingen-szb.com/',
        'https://www.gea.de/neckar-alb/kreis-tuebingen_artikel,-neues-angebot-in-Tübingen-sport-f%C3%BCr-eine-starke-psyche-_arid,6546433.html',
        'https://www.baunetzwissen.de/solar/objekte/sport-freizeit/paul-horn-arena-in-tuebingen-72834/',
        'https://zsl-bw.de/,Lde/Startseite/ueber-das-zsl/regionalstelle-tuebingen/',
        'https://www.zar.de/tuebingen/gesundheit-fitness/',
        'https://www.ndr.de/sport/Sieg-gegen-Tuebingen-Rostock-Seawolves-auf-Titelkurs,seawolves886.html',
        'https://www.antenne1.de/p/Sport-Mix-Camp-bei-den-Tigers-Tubingen-4g37htGTxNwpQfjeTVCMol/',
        'https://sport-nachgedacht.de/videobeitrag/ifs-der-uni-tuebingen/',
        'https://www.tvderendingen.de/',
        'https://tv-rottenburg.de/sportangebote/leichtathletik/details-leichtathletik/news/leichtathletik-5-kindersportfest-in-tuebingen/',
        'https://www.tuebinger-erbe-lauf.de/',
        'https://www.gesundheit-studieren.com/suche/bachelor-sport-gesundheit-tuebingen/',
        'https://netzwerk-onkoaktiv.de/institut/universitaetsklinikum-abteilung-sportmedizin-der-universitaetsklinik-tuebingen/',
        'https://tvstaufia.de/artikel/sport-und-kulturevent-in-tuebingen/',

        # company
        'https://www.medizin.uni-tuebingen.de/',
        'https://www.uni-tuebingen.de/',
        'https://www.cht.com/',
        'https://www.tuebingen.de/',
        'https://www.rp-tuebingen.de/',
        'https://www.kemmler.de/',
        'https://www.lwv-eh.de/',
        'https://www.erbe-med.com/',
        'https://www.walter-tools.com/',
        'https://www.phorn.de/',
        'https://www.tagblatt.de/',
        'https://www.udo-tuebingen.de/',
        'https://www.ksk-tuebingen.de/',
        'https://www.dkms.de/',
        'https://www.cht.com/',
        'https://www.curevac.com/',
        'https://www.swtue.de/',
        'https://www.roesch-fashion.com/',
        'https://www.osiander.de/',
        'https://www.dentalbauer.de/',
        'https://www.dentalbauer.de/',
        'https://www.mode-zinser.de/',
        'https://www.zeltwanger.de/',
        'https://www.vbidr.de/',
        'https://www.tropenklinik.de/',
        'https://www.science-computing.de/',
        'https://www.brennenstuhl.com/',
        'https://www.brillinger.de/',
        'https://www.baeckerei-gehr.de/',
        'https://www.immatics.com/',
        'https://www.itdesign.de/',
        'https://www.walter-machines.com/',
        'https://www.altenhilfe-tuebingen.de/',
        'https://www.syss.de/',
        'https://www.zeltwanger.de/',
        'https://www.itdesign.de/',
        'https://www.syss.de/',
        'https://www.curevac.com/',
        'https://www.solar-distribution.baywa-re.de/',
        'https://www.eurofins.de/',
        'https://www.nusser-schaal.de/',
        'https://www.cegat.de/',
        'https://www.roesch-fashion.com/',
        'https://www.tdmsystems.com/',
        'https://www.electroluxprofessional.com/',
        'https://www.bwva.de/',
        'https://www.suedweststrom.de/',
        'https://www.haertha.de/',
        'https://www.gmgcolor.com/',
        'https://www.avat.de/',
        'https://www.kocherlutz.de/',
        'https://www.bayer-kastner.de/',
        'https://www.phorn.de/',
        'https://www.kern-medical.com/',
        'https://www.teamplan.de/',
        'https://www.autohaus-seeger.de/',
        'https://www.bg-kliniken.de/',
        'https://www.team-training.de/',
        'https://www.ovesco.com/',
        'https://www.cumdente.com/',
        'https://www.gmgcolor.com/',
        'https://www.krone-tuebingen.de/',
        'https://www.mhp-pflege.de/',
        'https://www.zeutschel.de/',
        'https://www.dai-tuebingen.de/',
        'https://www.storymaker.de/',
        'https://www.pagina.gmbh/',
        'https://www.promotion-software.de/',
        'https://www.fliesen-kemmler.de/',
        'https://www.daasi.de/',
        'https://www.verifort-capital.de/',
        'https://www.topsim.com/',
        'https://www.karg-und-petersen.de/',
        'https://www.shs-capital.eu/',
        'https://www.dr-droescher.de/',
        'https://www.macfarlane.de/',
        'https://www.arsenalfilm.de/',
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
        'https://create.twitter.com',
    ]

    db = None

    def __init__(self, db) -> None:
        self.db = db
        self.user_agent = 'TuebingenExplorer/1.0'
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        self.min_depth_limit = 0
        self.max_depth_limit = 2
        self.max_threads = 4
        self.base_crawl_delay = 2.0
        # self.wordnet_local = threading.local()
        # self.wordnet_local.lock = threading.Lock()

        # If the frontier is empty, we load it with our initial frontier
        if self.db.check_frontier_empty():
            for link in self.initial_frontier:
                self.db.push_to_frontier(link)

    # Helper Functions
    def print_web_page(self, web_page):
        """
        Prints all details of the crawled web page.

        Parameters:
        - web_page (disctionary): The web page object.

        Returns:
        - None.
        """
        print(f"ID: {web_page['id']}")
        print(f"URL: {web_page['url']}")
        print(f"Title: {web_page['title']}")
        # print(f"Normalized Title: {web_page['normalized_title']}")
        # print(f"Keywords: {web_page['keywords']}")
        # print(f"Description: {web_page['description']}")
        # print(f"Normalized Description: {web_page['normalized_description']}")
        # print(f"Internal Links: {web_page['internal_links']}")
        # print(f"External Links: {web_page['external_links']}")
        # print(f"In Links: {web_page['in_links']}")
        # print(f"Out Links: {web_page['out_links']}")
        # print(f"Content: {web_page['content']}")
        # print(f"Image URL: {web_page['img']}")

        print("--------------------")

    def add_internal_links_to_frontier(self, url, internal_links):
        """
        Adds all the internal links to the frontier array.
        Parameters:
        - url (BeautifulSoup): The BeautifulSoup url.
        - internal_links (list):  A list of visited internal URLs

        Returns:
        - None
        """
        for link in internal_links:
            if link.startswith("/") or link.startswith(url):
                if link.startswith("/"):
                    link = urljoin(url, link)
                self.frontier.append(link)

    def crawl_url(self, url):
        """
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

                    try:
                        keywords = get_keywords(
                            content, normalized_title, normalized_description
                        )
                    except Exception as e:
                        print(
                            f"Exception occurred while keywords: {url} | {e}")

                    in_links = []

                    out_links = []

                    img = str(get_image_url(soup, url))

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
                        content,
                        img,
                    )

                    # Save to the database
                    with db_lock:
                        try:
                            entry = self.db.add_document(web_page)
                            # If the document is in the db already, we get None back
                            web_page['id'] = None if entry is None else entry[0]
                        except Exception as e:
                            self.print_web_page(web_page)
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
        threads = []
        while True:
            with db_lock:
                next_urls = self.db.get_from_frontier(self.max_threads)
                if next_urls is None:
                    break

            for url in next_urls:
                thread = CrawlThread(self, url)
                thread.start()
                threads.append(thread)

            # Wait for all remaining threads to complete
            for thread in threads:
                thread.join()

            with db_lock:
                for thread in threads:
                    self.db.remove_from_frontier(thread.url)
                    threads.remove(thread)

    def create_inout_links(self):
        """
        Populates the in_links and out_links fields in our database.
        """
        self.db.create_inoutlinks()


def get_sitemap_from_host(self, domain):
    """
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
    Gets the sitemap from the given domain.

    Parameters:
    - domain
    - self

    Returns:
    - list: the sitemap list of the domain.
    """
    with db_lock:
        try:
            # update the domain_internal_links
            self.db.update_domain_sitemap(domain, array_to_set)

        except Exception as e:
            print(f"Exception occurred while setting sitemap: {domain} | {e}")


def add_external_link_to_sitemap(self, domain_external_links):
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

        # print(f'DOMAIN: {domain}')
        # print(f'EXTERNAL: {external}')

        # add this link to the sitemap
        if external not in sitemap:
            sitemap.append(external)
            # write back sitemap
            set_sitemap_to_host(self, domain, sitemap)


def make_pretty_url(link):
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
    Checks if the language of a text is English.

    Parameters:
    - text (string): The Text to check.

    Returns:
    - bool: True if the language is German, False otherwise.
    """
    text = str(text)

    try:
        language_code = detect(text)
        return language_code == 'de'
    except:
        return False


# Crawler Functions


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
    img,
):
    """
    Creates a web page object.

    Parameters:
    - id (int): The ID of the web page.
    - index (int | none): The index of the web page.
    - url (str): The URL of the web page.
    - title (str): The title of the web page.
    - normalized_title (str): The normalized title of the web page.
    - keywords (list): The keywords generated from the content.
    - description (str): The description from the description meta tag.
    - normalized description (str): The normalized description from the description meta tag.
    - internal_links (list): A list of internal links (URLs within the same domain).
    - external_links (list): A list of external links (URLs outside the current domain).
    - in_links (list): An empty list to store incoming links from other pages.
    - out_links (list): A list of URLs extracted from anchor tags on the page.
    - content (str): The plain text content of the web page.
    - img (str): The URL to the thumbnail.

    Returns:
    - dictionary: A dictionary representing the web page object.
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
    Extracts the title of a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - str or None: The title of the web page if found, otherwise None.
    """
    title = soup.title.string if soup.title else None

    if title != None and is_text_english(title):
        return translate_german_to_english(title)
    else:
        return soup.title.string if soup.title else None


def get_keywords(content, normalized_title, normalized_description):
    """
    Extracts the keywords from the content using the RAKE algorithm.

    Parameters:
    - content (str): The text content to extract keywords from.
    - normalized_title (str): The normalized_title to extract keywords from.
    - normalized_description (str): The normalized_description to extract keywords from.

    Returns:
    - list: The extracted keywords as a list of single words.
    """

    concat = ""
    if content is not None:
        concat += content + " "
    if normalized_title is not None:
        concat += normalized_title
    if normalized_description is not None:
        concat += normalized_description

    keywords_a = kw_model.extract_keywords(concat, top_n=20)
    keywords = [normalize_text(key[0]) for key in keywords_a]

    return keywords


def translate_german_to_english(text):
    with translation_lock:
        text = str(text)
        translator = Translator(from_lang='de', to_lang='en')
        translation = translator.translate(text)
        return translation


def get_description(soup):
    """
    Extracts the description from the description meta tag of a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - str or None: The description from the meta tag if found, otherwise None.
    """
    description = soup.find('meta', attrs={'name': 'description'})
    if description and is_text_english(description):
        return translate_german_to_english(description['content'])
    else:
        return description['content'] if description else None


def has_tuebingen_content(url):
    user_agent = 'TuebingenExplorer/1.0'
    try:
        response = requests.get(url)

        # Check if the request is successful (status code 200)
        if response.status_code == 200:
            is_allowed = is_crawling_allowed(2.0, url, user_agent)
            if is_allowed[0]:
                # Use BeautifulSoup to parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')

                if (
                    'tuebingen' in str(soup)
                    or 'Tuebingen' in str(soup)
                    or 'tübingen' in str(soup)
                    or 'Tübingen' in str(soup)
                    or 'tubingen' in str(soup)
                    or 'Tubingen' in str(soup)
                ):
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
    Extracts the internal and external links from a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.
    - url (str): The URL of the web page.

    Returns:
    - tuple: A tuple containing two lists:
        - list: The internal links (URLs within the same domain).
        - list: The external links (URLs outside the current domain).
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
                #             else:
                #                 print(f'already in sitemap {external_link}')
                #         else:
                #             print(f'me myself and I {external_link}')
                #     else:
                #         print(f'max depth {external_link}')
                # else:
                #     print(f'blacklisted {external_link}')

                # add all internal links to web_page_property
                external_links.append(external_link)

                # Add the URL to the domain sitemap
                domain_external_links.append(external_link)

            elif not href.startswith('#') and not '#' in href:
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
                                with db_lock:
                                    # frontier push here
                                    # print(
                                    #     f'add internal link to frontier: {internal_link}'
                                    # )
                                    self.db.push_to_frontier(internal_link)
                #             else:
                #                 print(f'already in sitemap {internal_link}')
                #         else:
                #             print(f'me myself and I {internal_link}')
                #     else:
                #         print(f'max depth {internal_link}')
                # else:
                #     print(f'blacklisted {internal_link}')

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
    - str: The lemmatized and normalized content of the web page.
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

    if is_text_english(content):
        content = translate_german_to_english(content)

    return normalize_text(content)


def get_image_url(soup, url):
    """
    Extracts the og:twitter image URL or favicon URL from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.
    - url (str): The URL of the web page.

    Returns:
    - str: The og:image URL if found, otherwise the og:twitter image URL if found, otherwise the favicon URL, or an empty string if both are not found.
    """
    # Find the og:twitter image tag
    og_image_tag = soup.find("meta", attrs={"property": "og:image"})

    # Find the og:twitter image tag
    twitter_image_tag = soup.find("meta", attrs={"property": "twitter:imag"})

    # Find the favicon tag
    favicon_tag = soup.find("link", rel="icon")

    # Extract the og:image image URL
    if og_image_tag is not None:
        og_image_url = og_image_tag.get("content", "")
        if og_image_url:
            return (
                og_image_url
                if og_image_url.startswith('http')
                else 'https:' + og_image_url
            )

    # Extract the twitter:image URL
    elif twitter_image_tag is not None:
        og_image_url = twitter_image_tag.get("content", "")
        if og_image_url:
            return (
                og_image_url
                if og_image_url.startswith('http')
                else urljoin(url, '/')[:-1] + og_image_url
            )

    # Extract the favicon URL
    elif favicon_tag is not None:
        favicon_url = favicon_tag.get("href", "")
        if favicon_url:
            return urljoin(url, '/')[:-1] + favicon_url

    return ""


def pos_tagger(tag):
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
    # Remove special characters and lowercase the content
    content = re.sub(r'[^\w\s]', '', input).lower()

    # Normalize German characters to English equivalents
    content = normalize_german_chars(content)

    # Tokenize the content
    tokens = word_tokenize(content)

    # Remove stopwords
    stopwords_set = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stopwords_set]

    # Get tags on each word
    token_pos_tags = nltk.pos_tag(filtered_tokens)
    wordnet_tag = map(lambda x: (x[0], pos_tagger(x[1])), token_pos_tags)
    lemmatized_content = []

    with wordnet_lock:
        # Lemmatize the content
        lemmatizer = WordNetLemmatizer()

        for word, tag in wordnet_tag:
            if tag is None:
                lemmatized_content.append(word)
            else:
                lemmatized_content.append(lemmatizer.lemmatize(word, tag))

    # Convert the lemmatized content back to a string
    return ' '.join(lemmatized_content)
