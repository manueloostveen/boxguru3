FLESSEN_DOZEN = 'Flessendozen'
VEILIGHEIDS_DOZEN = 'Extra veilige dozen'
SPECIALE_DOZEN = 'Speciale dozen'
ENVELOPPEN = 'Enveloppen'
VERZENDZAKKEN = 'Verzendzakken'
VERZENDKOKERS = 'Verzendkokers'
OVERIG = 'Overig'
VERZEND_DOZEN = 'Verzenddozen'
WIKKEL_DOZEN = 'Boek- en kruiswikkelverpakkingen'
VERHUIS_DOZEN = 'Verhuis-, ordner- en archiefdozen'
VARIABELE_DOZEN = 'In hoogte verstelbare dozen'
VOUWDOZEN = 'Vouwdozen'
KISTEN = 'Kisten/kratten'
OVERIGE_DOZEN = 'Overige dozen'
PALLET_DOZEN = 'Palletdozen'
OVERIG = 'Overig'
KOEL_DOZEN = 'Koeldozen'

product_category_dict = {
    'FLESSEN_DOZEN': FLESSEN_DOZEN,
    'VEILIGHEIDS_DOZEN': VEILIGHEIDS_DOZEN,
    'SPECIALE_DOZEN': SPECIALE_DOZEN,
    'ENVELOPPEN': ENVELOPPEN,
    'VERZENDZAKKEN': VERZENDZAKKEN,
    'VERZENDKOKERS': VERZENDKOKERS,
    'OVERIG': OVERIG,
    'VERZEND_DOZEN': VERZEND_DOZEN,
    'WIKKEL_DOZEN': WIKKEL_DOZEN,
    'VERHUIS_DOZEN': VERHUIS_DOZEN,
    'VARIABELE_DOZEN': VARIABELE_DOZEN,
    'VOUWDOZEN': VOUWDOZEN,
    'KISTEN': KISTEN,
    'OVERIGE_DOZEN': OVERIGE_DOZEN,
    'PALLET_DOZEN': PALLET_DOZEN,
}

box_main_category_dict = {
    'FLESSEN_DOZEN': FLESSEN_DOZEN,
    'VEILIGHEIDS_DOZEN': VEILIGHEIDS_DOZEN,
    'SPECIALE_DOZEN': SPECIALE_DOZEN,
    'VERZEND_DOZEN': VERZEND_DOZEN,
    'WIKKEL_DOZEN': WIKKEL_DOZEN,
    'VERHUIS_DOZEN': VERHUIS_DOZEN,
    'VARIABELE_DOZEN': VARIABELE_DOZEN,
    'VOUWDOZEN': VOUWDOZEN,
    'KISTEN': KISTEN,
    'OVERIGE_DOZEN': OVERIGE_DOZEN,
    'PALLET_DOZEN': PALLET_DOZEN,
    'KOEL_DOZEN': KOEL_DOZEN,
}

fit_box_category_dict = {
    'FLESSEN_DOZEN': FLESSEN_DOZEN,
    'VEILIGHEIDS_DOZEN': VEILIGHEIDS_DOZEN,
    'SPECIALE_DOZEN': SPECIALE_DOZEN,
    'VERZEND_DOZEN': VERZEND_DOZEN,
    'WIKKEL_DOZEN': WIKKEL_DOZEN,
    'VERHUIS_DOZEN': VERHUIS_DOZEN,
    'VOUWDOZEN': VOUWDOZEN,
    'KISTEN': KISTEN,
    'OVERIGE_DOZEN': OVERIGE_DOZEN,
    'PALLET_DOZEN': PALLET_DOZEN,
}

box_main_categories = {
    8: [(125, 'UN-dozen'), (97, 'Fixeer-Zweefverpakkingen'), (113, 'Schuimdozen')], #Extra veilige dozen
    1: [(94, 'Autolockdozen'), (103, 'Dekseldozen'), (90, 'Standaard-dozen')], #Vouwdozen
    7: [(109, 'Bierdozen'), (96, 'Flessendozen'), (104, 'Wijndozen')], #Flessendozen
    4: [(91, 'Brievenbusdozen'), (99, 'Envelobox'), (131, 'Postdozen')], #Verzenddozen
    5: [(112, 'Geschenkdozen'), (123, 'Giftcarddozen'), (124, 'Gondeldozen'), (121, 'Magneetdozen')], #Speciale dozen
    16: [(119, 'Koeldozen')], #Koeldozen
    9: [(108, 'Kruiswikkel-Boekverpakkingen')], #Kruiswikkel/boekverpakkingen
    2: [(101, 'Ordnerdozen'), (106, 'Verhuisdozen')], #Verhuis/order/archiefdozen
    3: [(98, 'Palletdozen')], #Palletdozen
    10: [(122, 'Schuifdozen')] #Overige dozen











}
box_categories = [125, 94, 109, 91, 103, 99, 97, 96, 112, 123, 124, 119, 108, 121, 101, 98, 131, 122, 113, 90, 106, 104]

not_box_main_category_dict = {
    'OVERIG': OVERIG,
    'VERZENDZAKKEN': VERZENDZAKKEN,
    'ENVELOPPEN': ENVELOPPEN,
    'VERZENDKOKERS': VERZENDKOKERS,
}
