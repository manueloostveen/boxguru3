from django import template
from boxguru.settings import TEXT_FILES_ROOT
from products import category_texts

register = template.Library()

VOUWDOZEN = 'Goedkope vouwdozen van bruin karton zijn geschikt voor het verzenden van middelgrote en grote producten van allerlei aard. Onder vouwdozen vallen bij BoxGuru de standaard dozen of Amerikaanse vouwdozen, dekseldozen en autolockdozen met een automatische bodem. De dozen zijn volgens verschillende standaarden ontworpen en zijn beschikbaar in verschillende wanddiktes golfkarton: enkelwandig, dubbelwandig of driedubbelwandig. De vouwdozen zijn verkrijgbaar in vele verschillende maten. De grote vouwdozen worden voorgelijmd en vlak geleverd, zodat ze gemakkelijk met tape kunnen worden gesloten met behulp van de bodem- en dekselkleppen. Een paar voordelen van vouwdozen onder elkaar: Vouwdozen bieden de best mogelijke bescherming voor uw producten op de post. Verschillende afmetingen van de beschikbare vouwdozen. Vouwdozen beschermen uw producten tegen milieu-invloeden. Vouwdozen zijn geschikt voor automatisch en handmatig order picken. Vouwdozen zijn stapelbaar en kunnen goed worden opgeslagen.'
EXTRA_VEILIGE_DOZEN = 'Onder extra veilige dozen vallen zowel de dozen die geschikt zijn om gevaarlijke stoffen of goederen te vervoeren als dozen die speciaal voor breekbare artikelen zijn gemaakt. Voor gevaarlijke stoffen zijn UN dozen te vinden. Dit zijn kartonnen vouwdozen die gekeurd zijn aan huidige wet- en regelgeving voldoen. Voor breekbare producten zijn bij BoxGuru fixeerdozen en schuimdozen te vinden. Beide dozen zorgen ervoor dat het verpakte product op zijn plek blijft. Schuimdozen zijn voorzien van een dikke laag zacht schuim aan de binnenzijde van de doos.'
LUXE_GESCHENKDOZEN = 'Soms is de doos belangrijker dan de inhoud. Als je echt op wilt vallen kun je voor kartonnen geschenkdozen kiezen. Onder geschenkdozen vallen bij BoxGuru de feestelijk bedrukte verzenddoosjes, giftcarddozen, gondeldoosjes en magneetdozen.'
FLESSENDOZEN = 'Flessendozen zijn extra stevige dozen die precies het formaat hebben voor een bepaald aantal flessen. De kartonnen dozen komen in verschillende types en wanddiktes. Vooral de flessendoos van dubbelgolf karton is extra veilig tijdens transport en opslag. Flessendozen kunnen vaak nog extra veilig gemaakt worden door een speciaal flesseninterieur bij de doos te kopen. Dit interieur van geperst karton past precies in de doos en zorgt ervoor dat de dozen veiliger gestapeld en verzonden kunnen worden.'
VERZENDDOZEN = 'Of u nu verzenddozen gebruikt om producten twee blokken verderop te leveren of een geschenk naar een vriendin te sturen, het kiezen van de juiste vorm, grootte, type en materiaal is een belangrijk onderdeel van het verzendproces. BoxGuru heeft een aantal verzenddozen en benodigdheden voor het verplaatsen van diverse goederen verzameld. De vorm van een verzenddoos moet zoveel mogelijk overeenkomen met de items die erin gaan om lege ruimtes te beperken en om te voorkomen dat er te veel wordt gevuld, wat tot schade zou kunnen leiden. Veel merken bieden verschillende vormen aan om aan verschillende verzendingsbehoeften te voldoen. Onder verzenddozen vallen bij BoxGuru de postdozen, brievenbusdozen en de envelobox. Kies een verzenddoos met een variabele hoogte als je nog niet weet hoe groot het product is dat verpakt moet worden. Deze dozen zijn voorzien van geperforeerde lijnen om te helpen om de perfecte pasvorm te krijgen; snijd gewoon langs de lijn voor de gewenste diepte. De meeste dozen zijn van golfkarton, dit kan enkel, dubbel of driedubbel karton zijn. Enkelwandige golfkartonnen dozen zijn geschikt voor artikelen die minder dan 30 kg wegen. Enkellaagse kartonnen dozen zijn alleen veilig voor het verzenden van kleine, lichtgewicht items. Als u overzees wilt verzenden of zware of breekbare items die extra bescherming nodig hebben, overweeg dan heavy-duty dubbelwandige golfkartonnen dozen. Deze zijn ook stevig genoeg voor het stapelen van meerdere dozen op elkaar. Gebruik altijd dubbelwandige containers voor voorwerpen die 40 kg of meer wegen. Veel verzenddozen gebruiken tussen 30 en 100 procent gerecycled materiaal. Denk ook aan milieuvriendelijk materiaal om uw pakket te beveiligen. Biologisch afbreekbaar verpakkingsmateriaal is een milieuvriendelijk product dat een goed alternatief is voor plastic bubbeltjesfolie voor de binnenbekleding. Het is raadzaam om een nieuwe doos te gebruiken wanneer dat mogelijk is. Verzenddozen zullen bij elk gebruik slijten. Als u er een moet hergebruiken, zorg er dan voor dat deze vrij is van scheuren en gaten en geen waterschade heeft die het materiaal zal verzwakken. U kunt dozen verzegelen met verpakkingstape of zelfsluitende lipjes. De tape moet minimaal 5 cm breed zijn en minimaal 2,5 cm over de randen van de doos uitsteken. Gebruik zelfsluitende lipjes zoals ze zijn of met tape voor extra veiligheid.'

AUTOLOCKDOZEN = 'Autolockdozen zijn stevige kartonnen vouwdozen met een automatische bodem. Autolock dozen worden vaak gebruikt door webwinkels en andere bedrijven die graag tijd besparen tijdens het inpakken van hun pakketten. Autolockdozen zijn in een handomdraai uit te vouwen en kunnen eenvoudig gesloten worden, soms doormiddel van een zelfklevende sluiting met scheurstrip. Dit maakt het afsluiten van dit soort kartonnen dozen extra makkelijk en snel. Voor de ontvanger is de scheurstrip een handige toevoeging. Hierdoor zijn autolockdozen makkelijk te openen nadat het pakket ontvangen is.'
DEKSELDOZEN = 'Dekseldozen bestaan uit een bodem en een deksel die naadloos over elkaar passen. Dekseldozen van karton zijn vaak speciaal gemaakt voor het verpakken van papier en drukwerk. De dozen komen daarom in standaardformaten (A4, A5, A6, etc). Doordat dit soort dozen een schuifbare deksel hebben onstaat er een variabele vulhoogte. Dekseldozen worden plat aangeleverd en zijn snel en eenvoudig in uit te vouwen en in elkaar te zetten. Naast het verpakken van papier zijn dekseldozen ook geschikt voor het verzenden over opslaan van andere producten. Bijvoorbeeld schoenen, kleding en electronica.'
STANDAARDDOZEN = 'De standaard doos, ook wel de Amerikaanse vouwdoos (Fefco 0201) is de ideale doos om producten mee te verzenden. De kartonnen Amerikaanse vouwdoos wordt gezien als de standaard doos. Een eenvoudigere kartonnen doos bestaat er niet. Standaard vouwdozen zijn gemaakt van golfkarton. Dit kan enkelvoudig, dubbel of driedubbel golfkarton zijn. De doos wordt eenvoudig in elkaar gevouwen door de kleppen aan de onder en bovenzijde met tape dicht te plakken. Dit soort stevige kartonnen dozen beschermen jouw producten optimaal tijdens het transport en tijdens opslag. Omdat vouwdozen in zoveel verschillende uitvoeringen komen zijn ze geschikt voor verschillende producten: Consumenten electronica, laptop accecoires, sieraden en andere soorten artikelen. '
VERHUISDOZEN = 'Verhuisdozen zijn speciaal gemaakt voor verhuizingen. Verhuisdozen zijn dozen die geschikt zijn om zwaar te belasten en hebben een vlakke bodem die volledig dicht is.  Dit soort kartonnen dozen zijn zo stevig omdat zij vaak gemaakt worden van dubbelgolf karton. De dozen hebben aan de bovenzijde vaak twee kleppen met een inkeping waardoor er geen tape of ander afsluitmateriaal nodig is om de verhuisdozen af te sluiten.  Om het tillen van de dozen makkelijker te maken zijn verhuisdozen voorzien van handvaten.'
ARCHIEFDOZEN = 'Archiefdozen zijn speciaal geschikt voor het bewaren of verzenden van documenten, ordners of ringmappen. De dozen zijn eenvoudig in elkaar te zetten. Ordnerdozen zijn kruiswikkelverpakkingen die speciaal gemaakt zijn voor het verpakken van ordners of ringmappen. Meestal voorzien van een zelfklevende sluitstrip.'
PALLETDOZEN = 'Palletdozen zijn groot formaat kartonnen dozen die precies op een europallet of blokpallet passen. In de palletdoos worden vaak weer kleinere kartonnen dozen gedaan. De palletdoos dient als extra bescherming en komt in verschillende wanddiktes. Dit kan enkelgolf, dubbelgolf of driedubbelgolf karton zijn. Dit maakt palletdozen extra sterk en geschikt voor langdurig opslag of transport. Palletdozen komen in verschillende uitvoeringen, soms met laadklep. Sommige pallet dozen bestaan uit meerdere onderdelen die in elkaar passen.'
BRIEVENBUSDOZEN = 'Brievenbusdozen zijn verzenddozen of postdozen die klein genoeg zijn om door de brievenbus te passen. Platte producten als boeken, mobiele telefoons of sieraden. Doordat de kartonnen doosjes precies door de brievenbus passen hoeven er minder verzendkosten betaald te worden. Dit is erg aantrekkelijk als je kleine producten verkoopt. Brievenbusdozen zijn daarom uitermate geschikt voor webshops en e-commerce.  De standaard brievenbusdoos heeft een makkelijk te sluiten bovenklep en komt soms met een zelfklevende sluit- of retourstrip.'
ENVELOBOX = 'De Envolobox is een combinatie tussen een kartonnen doos en een stevige envelop. De doos is eenvoudig te vullen en te sluiten door middel van de sluitstrip. De Envelobox past door de brievenbus en is geschikt voor retourzendingen. Waar normale enveloppen te weinig bescherming bieden is de Envelobox de ideale oplossing.'
POSTDOZEN = 'Op BoxGuru is een grote hoeveelheid kartonnen postdoosjes te vinden. De postdoos is een van de stevigste verzenddozen die er te vinden is. De dozen worden geleverd als gestansde platte platen; ze worden daarna opgevouwen tot een stevige verpakking met driedubbel dikke zijwanden en een deksel met een lipje dat netjes in de doos zelf past. Hierdoor kan de postdoos snel en eenvoudig afgesloten worden. Dit maakt de doos niet alleen ideaal voor verzenden en transport maar ook voor het opslaan van artikelen. Postdozen met bovenklep komen in een groot aantal verschillende typen, formaten en kleuren. Met een postdoos in kleur is het mogelijk extra op te vallen. Postdozen hebben ook vaak een zelfklevende sluitstrip met scheurperforatie. Dit maakt deze kartonnen doosjes ideaal voor retourzendingen. Postdoosjes worden daarom vaak gebruikt door webshops en e-commerce bedrijven.'
GESCHENKDOZEN = 'Onder geschenkdozen vallen bij BoxGuru de feestelijk bedrukte verzenddoosjes. Denk aan dozen met een kerst of sinterklaas thema. Deze bedrukte dozen zijn gemaakt om op te vallen.'
GIFTCARDDOZEN = 'Giftcard dozen zijn luxe verpakkingen voor cadeaubonnen of gift cards. De doosjes hebben een inlay waar een tegoedbon of gift card in past.'
GONDELDOZEN = 'De gondeldoos is een veelzijdige geschenkverpakking in een opvallende gondelvorm. De doosjes zijn eenvoudig open te vouwen, te vullen en weer af te sluiten. Gondeldoosjes zijn ideaal om kadobonnen, juwelen, sieraden en andere kleine producten in te verpakken.'
MAGNEETDOZEN = 'Magneetdozen zijn luxe geschenkverpakkingen met een magneetsluiting.'
WIJNDOZEN = 'Wijndozen hebben precies de juiste afmeting voor een bepaalde hoeveelheid wijnflessen (vaak 1,2,3,4,6 of 12 flessen van 0,75L). De dozen worden vaak voorzien van een (niet bijgeleverd) insert of interieur die de flessen extra bescherming bieden. Vergeet niet het interieur los bij te bestellen. BoxGuru heeft alleen de wijndozen voor je gevonden, het interieur moet je er soms nog bij kopen, dit is niet altijd inclusief. '
BIERDOZEN = 'Bierdozen zijn kartonnen vouwdozen die speciaal gemaakt zijn om bierflesjes in te verpakken.'
UNDOZEN = 'UN dozen zijn dozen met een UN keurmerk. UN dozen zijn speciaal gemaakt om gevaarlijke stoffen of goederen te bewaren en te vervoeren. De UN dozen komen in een aantal verschillende maten en zijn gemaakt van '
FIXEERDOZEN = 'Fixeerverpakkingen en zweefverpakkingen zijn kartonnen verzendverpakkingen die voorzien van extra schuim of folie. De extra versteviging zorgt voor goede fixatie van het te verzenden product en zijn extra schokbestendig.'
SCHUIMDOZEN = 'Schuimdozen zijn verzenddozen die zijn voorzien van een dikke laag schuim aan de binnenzijde, deze dozen zijn uitermate geschikt voor het verzenden van kwetsbare producten.'
KRUISWIKKEL = 'Kruiswikkelverpakkingen of boekverpakkingen zijn uitermate geschikt voor het verpakken van boeken of vergelijkbare producten. Doordat het boek in de verpakking wordt "gewikkeld" heeft de verpakking een variabele hoogte. Wikkelverpakkingen zijn vaak voorzien van een zelfklevende sluitstrip.'
SCHUIFDOZEN = 'Schuifdozen bestaan uit twee delen, een omdoos en een bodem. De twee onderdelen zijn eenvoudig in elkaar te schuiven.'
KOELDOZEN = 'Koeldozen zijn uitermate geschikt voor het vervoeren of verzenden van gekoelde of bevroren producten. De dozen worden van speciaal isolerend materiaal gemaakt, dit kan EPS, tempex of piepschuim zijn.'

get_text_main_category = {
    1: VOUWDOZEN,
    4: VERZENDDOZEN,
    7: EXTRA_VEILIGE_DOZEN,
    5: LUXE_GESCHENKDOZEN,
    6: FLESSENDOZEN,
    11: VERHUISDOZEN,
    2: ARCHIEFDOZEN,
    3: PALLETDOZEN,
    8: KRUISWIKKEL,
    9: SCHUIFDOZEN,
    10: KOELDOZEN,
}

get_text_sub_category = {
    1: AUTOLOCKDOZEN,
    2: DEKSELDOZEN,
    3: STANDAARDDOZEN,
    7: BRIEVENBUSDOZEN,
    8: ENVELOBOX,
    9: POSTDOZEN,
    10: GESCHENKDOZEN,
    11: GIFTCARDDOZEN,
    12: GONDELDOZEN,
    13: MAGNEETDOZEN,
    15: WIJNDOZEN,
    14: BIERDOZEN,
    16: UNDOZEN,
    17: FIXEERDOZEN,
}

SMALL_AUTOLOCKDOZEN = 'Autolockdozen zijn extra snel in elkaar te vouwen door hun automatische bodem. Autolock dozen worden vaak gebruikt door webwinkels en andere bedrijven die graag tijd besparen tijdens het inpakken van hun pakketten. De dozen zijn in een handomdraai uit te vouwen en kunnen eenvoudig gesloten worden, soms doormiddel van een zelfklevende sluiting.'
SMALL_DEKSELDOZEN = 'Dekseldozen bestaan uit twee delen die naadloos over elkaar passen. De dozen zijn snel in elkaar te zetten en hebben een variabele vulhoogte.'
SMALL_STANDAARDDOZEN = 'De Amerikaanse vouwdoos (Fefco 0201) wordt gezien als de standaard doos en is de ideale doos voor opslag of om producten mee te verzenden. De doos heeft aan twee kanten kleppen die worden dichtgevouwen en afgesloten met tape.'
SMALL_ORDNERDOZEN = 'Ordnerdozen zijn kruiswikkelverpakkingen die speciaal gemaakt zijn voor het verpakken van ordners of ringmappen. Meestal voorzien van een zelfklevende sluitstrip.'
SMALL_VERHUISDOZEN = 'Verhuisdozen zijn extra stevige kartonnen dozen, speciaal gemaakt om mee te verhuizen. De dozen zijn zwaar te belasten en hebben een vlakke bodem die volledig dicht is. De dozen zijn voorzien van handvaten en vaak van dubbelgolf karton.'
SMALL_ARCHIEFDOZEN = 'Archiefdozen worden gebruikt om documenten, ordners of ringmappen te bewaren of te verzenden. De dozen zijn eenvoudig in elkaar te zetten.'
SMALL_PALLETDOZEN = 'Palletdozen passen precies op een europallet of blokpallet. De dozen zijn extra sterk en geschikt voor langdurig opslag of transport. Palletdozen komen in verschillende soorten, soms bestaan ze uit meerderde delen en hebben een laadklep.'
SMALL_BRIEVENBUSDOZEN = 'Brievenbusdoosjes zijn kleine postdozen die door de brievenbus passen. Brievenbusdoosjes zijn makkelijk te sluiten door middel van de bovenklep en komen soms met een zelfklevende sluit- of retourstrip.'
SMALL_ENVELOBOX = 'De Envolobox is eenvoudig te vullen en te sluiten door middel van de sluitstrip. De Envelobox past door de brievenbus en is geschikt voor retourzendingen.'
SMALL_POSTDOZEN = 'Postdozen met klepsluiting of bovenklep zijn uitermate geschikt voor webshops. De dozen zijn eenvoudig uit te vouwen en af te sluiten en zijn erg stevig. Postdozen komen vaak met zelfklevende sluit- en retourstrip.'
SMALL_GESCHENKDOZEN = 'Onder geschenkdozen vallen de feestelijk bedrukte verzenddoosjes. Denk aan dozen met een kerst of sinterklaas thema'
SMALL_GIFTCARDDOZEN = 'Giftcard dozen zijn luxe verpakkingen voor cadeaubonnen of gift cards. De doosjes hebben een inlay waar een tegoedbon of gift card in past.'
SMALL_GONDELDOZEN = 'De gondeldoos is een veelzijdige geschenkverpakking in een opvallende gondelvorm. De doosjes zijn eenvoudig open te vouwen, te vullen en weer af te sluiten.'
SMALL_MAGNEETDOZEN = 'Magneetdozen zijn luxe geschenkverpakkingen met een magneetsluiting.'
SMALL_BIERDOZEN = ''
SMALL_WIJNDOZEN = 'Wijndozen hebben precies de juiste afmeting voor een bepaalde hoeveelheid wijnflessen. De dozen worden vaak voorzien van een (niet bijgeleverd) insert die de flessen extra bescherming bieden.'
SMALL_UNDOZEN = 'UN dozen zijn dozen met een UN keurmerk. UN dozen zijn speciaal gemaakt om gevaarlijke stoffen of goederen te bewaren en te vervoeren.'
SMALL_FIXEERDOZEN = 'Fixeerverpakkingen en zweefverpakkingen zijn kartonnen verzendverpakkingen die voorzien van extra schuim of folie. De extra versteviging zorgt voor goede fixatie van het te verzenden product en zijn extra schokbestendig.'
SMALL_SCHUIMDOZEN = 'Schuimdozen zijn verzenddozen die zijn voorzien van een dikke laag schuim aan de binnenzijde, deze dozen zijn uitermate geschikt voor het verzenden van kwetsbare producten.'
SMALL_KRUISWIKKEL = 'Kruiswikkelverpakkingen of boekverpakkingen zijn uitermate geschikt voor het verpakken van boeken of vergelijkbare producten. Doordat het boek in de verpakking wordt "gewikkeld" heeft de verpakking een variabele hoogte. Wikkelverpakkingen zijn vaak voorzien van een zelfklevende sluitstrip.'
SMALL_VERZENDDOZEN = ''
SMALL_VOUWDOZEN = ''
SMALL_EXTRA_VEILIGE_DOZEN = ''
SMALL_FLESSENDOZEN = ''
SMALL_LUXE_GESCHENKDOZEN = ''
SMALL_SCHUIFDOZEN = category_texts.SCHUIFDOZEN
SMALL_KOELDOZEN = category_texts.KOELDOZEN


get_small_text_sub_category = {
    1: SMALL_AUTOLOCKDOZEN,
    2: SMALL_DEKSELDOZEN,
    3: SMALL_STANDAARDDOZEN,
    7: SMALL_BRIEVENBUSDOZEN,
    8: SMALL_ENVELOBOX,
    9: SMALL_POSTDOZEN,
    10: SMALL_GESCHENKDOZEN,
    11: SMALL_GIFTCARDDOZEN,
    12: SMALL_GONDELDOZEN,
    13: SMALL_MAGNEETDOZEN,
    15: SMALL_WIJNDOZEN,
    14: SMALL_BIERDOZEN,
    16: SMALL_UNDOZEN,
    17: SMALL_FIXEERDOZEN,
}

get_small_text_main_category = {
    1: SMALL_VOUWDOZEN,
    4: SMALL_VERZENDDOZEN,
    7: SMALL_EXTRA_VEILIGE_DOZEN,
    5: SMALL_LUXE_GESCHENKDOZEN,
    6: SMALL_FLESSENDOZEN,
    11: SMALL_VERHUISDOZEN,
    2: SMALL_ARCHIEFDOZEN,
    3: SMALL_PALLETDOZEN,
    8: SMALL_KRUISWIKKEL,
    9: SMALL_SCHUIFDOZEN,
    10: SMALL_KOELDOZEN,
}


@register.filter('seo_text_subcategory')
def get_seo_text_subcategory(category_number):
    return get_text_sub_category.get(category_number)


@register.filter('seo_text_maincategory')
def get_seo_text_maincategory(category_number):
    return get_text_main_category.get(category_number)

@register.filter('small_text_subcategory')
def get_small_text_subcategory(category_number):
    return get_small_text_sub_category.get(category_number)

@register.filter('small_text_maincategory')
def get_small_text_subcategory(category_number):
    return get_small_text_main_category.get(category_number)