#!/usr/bin/env python3
"""Generate complete training dataset with 245 samples (35 per class)"""
import csv

data = []

# Blood test (35 samples)
blood_tests = [
    "Résultats analyse sanguine: Hémoglobine 14.5 g/dL, Globules rouges 4.8M/mm³, Leucocytes 7200/mm³, Plaquettes 250000/mm³",
    "Hémogramme complet: Hb 13.2 g/dL, Hématocrite 40%, VGM 88 fL, TCMH 30 pg, CCMH 34%",
    "Bilan sanguin: Sodium 140 mmol/L, Potassium 4.2 mmol/L, Chlore 102 mmol/L, Bicarbonates 25 mmol/L",
    "NFS: Leucocytes 6800/mm³, Neutrophiles 65%, Lymphocytes 28%, Monocytes 5%, Eosinophiles 2%",
    "Analyse sanguine biochimique: ASAT 28 UI/L, ALAT 32 UI/L, Gamma GT 18 UI/L, PAL 75 UI/L",
    "Glycémie à jeun 0.95 g/L, Hémoglobine glyquée 5.8%, Insulinémie 12 mUI/L",
    "Bilan lipidique: Cholestérol total 1.85 g/L, HDL 0.55 g/L, LDL 1.10 g/L, Triglycérides 0.85 g/L",
    "Fer sérique 95 µg/dL, Ferritine 120 ng/mL, Transferrine 250 mg/dL, Coefficient saturation 30%",
    "Numération formule sanguine: GR 4.5M/mm³, GB 7500/mm³, Plaquettes 280000/mm³",
    "Hémoglobine 15.2 g/dL, Hématocrite 45%, Réticulocytes 80000/mm³",
    "Ionogramme sanguin: Na 138 mmol/L, K 4.0 mmol/L, Ca 2.35 mmol/L, Mg 0.82 mmol/L",
    "VS 8 mm première heure, CRP 3 mg/L, Fibrinogène 3.2 g/L",
    "Fonction rénale: Créatinine 85 µmol/L, Urée 0.35 g/L, Clairance MDRD 95 mL/min",
    "Bilan hépatique: Bilirubine totale 10 µmol/L, Bilirubine conjuguée 3 µmol/L, PAL 68 UI/L",
    "Protéines totales 72 g/L, Albumine 42 g/L, Globulines 30 g/L",
    "Plaquettes 245000/mm³, VPM 8.5 fL, Temps Quick 85%, INR 1.1",
    "Leucocytes 8200/mm³ avec formule normale, Pas de cellules anormales",
    "GR 5.1M/mm³, Hb 16.5 g/dL chez homme 45 ans, Hématocrite 48%",
    "TSH 2.5 mUI/L, T3 libre 4.2 pmol/L, T4 libre 15 pmol/L",
    "Cortisol 8h: 420 nmol/L, ACTH 35 pg/mL",
    "LDH 180 UI/L, CPK 95 UI/L, Troponine <0.01 ng/mL",
    "Calcium ionisé 1.22 mmol/L, Phosphore 1.05 mmol/L, PTH 42 pg/mL",
    "Vitamine D 45 ng/mL, Vitamine B12 350 pg/mL, Folates 8 ng/mL",
    "GGT 22 UI/L, 5-nucléotidase 6 UI/L",
    "Amylase 65 UI/L, Lipase 42 UI/L",
    "Urée plasmatique 0.38 g/L, Acide urique 48 mg/L",
    "CRP ultrasensible 1.8 mg/L",
    "Electrophorèse protéines: Albumine 60%, Alpha1 3%, Alpha2 8%, Beta 12%, Gamma 17%",
    "Complément C3 1.15 g/L, C4 0.28 g/L",
    "IgG 12 g/L, IgA 2.5 g/L, IgM 1.2 g/L",
    "Numération plaquettaire 265000/mm³ normale",
    "Temps céphaline 32 sec, TP 90%",
    "Fibrinogène 3.5 g/L, D-dimères 0.3 mg/L",
    "Réticulocytes 75000/mm³ soit 1.5%",
    "Frottis sanguin: GR normocytaires normochromes"
]

xrays = [
    "Radiographie thoracique face: Poumons clairs sans opacité, Cœur taille normale",
    "Radio poignet droit: Fracture non déplacée radius distal",
    "Radio genou gauche: Pincement interligne, Ostéophytes marginaux, Gonarthrose grade 2",
    "Radio panoramique dentaire: 32 dents présentes, Caries 16-26-36",
    "Radio colonne lombaire: Arthrose L4-L5, Pincement discal L5-S1",
    "Thorax face-profil: Parenchyme pulmonaire normal, Silhouette cardiaque régulière",
    "Radio main gauche: Déminéralisation diffuse, Pincement inter-phalangien",
    "Radio bassin face: Coxarthrose bilatérale, Pincement interligne coxo-fémoral",
    "Radio cheville droite: Fracture malléole externe, Trait oblique",
    "Thorax: Syndrome alvéolaire base droite, Pneumopathie franche lobaire",
    "Radio crâne face-profil: Voûte et base normales, Sinus clairs",
    "Rachis cervical: Arthrose unco-vertébrale C5-C6",
    "ASP: Niveaux hydro-aériques grêle, Occlusion intestinale",
    "Radio épaule gauche: Tendinopathie calcifiante, Calcification 8mm",
    "Sinus face: Opacité sinus maxillaire droit, Sinusite",
    "Radio avant-bras: Fracture diaphysaire ulna",
    "Thorax: Epanchement pleural droit abondant",
    "Radio pied: Hallux valgus bilatéral, Angle 35°",
    "Rachis dorsal: Cyphose accentuée, Tassements D8-D10",
    "Radio sacrum coccyx: Coccygodynie, Luxation coccygienne",
    "Sternum profil: Fracture corporéale médiane",
    "Côtes: Fractures côtes 6-7-8 gauches",
    "Radio jambe: Fracture tibia tiers moyen",
    "Clavicule: Fracture tiers moyen",
    "Scapula: Fracture col scapulaire",
    "Poignet: Fracture scaphoïde, Trait oblique",
    "Radio hanche: Fracture col fémoral Garden 3",
    "Fémur: Fracture diaphysaire, Trait spiroïde",
    "Genou: Fracture plateau tibial latéral",
    "Rotule: Fracture polaire inférieure",
    "Cheville: Fracture bimalléolaire",
    "Calcanéus: Fracture thalamique",
    "Métatarses: Fracture Jones base 5ème",
    "Rachis lombaire: Spondylolyse L5",
    "Sacro-iliaques: Sacro-iliite bilatérale"
]

mris = [
    "IRM cérébrale gadolinium: Séquences T1-T2-FLAIR, Pas processus expansif, Normal",
    "IRM rachis lombaire: Discopathie L4-L5-L5-S1, Protrusion L5-S1",
    "IRM genou droit: Lésion méniscale médiale grade III, Chondropathie grade II",
    "IRM épaule gauche: Tendinopathie calcifiante supra-épineux 8mm",
    "IRM hépatique: Foie normal, Pas lésion focale",
    "IRM cérébrale: Hypersignaux FLAIR substance blanche, Leucoaraïose modérée",
    "IRM prostate multiparamétrique: Lésion zone périphérique PI-RADS 4",
    "IRM mammaire: Prise contraste nodulaire 12mm ACR 5",
    "IRM cardiaque: FEVG 55%, Hypokinésie apicale",
    "IRM rachis cervical: Hernie discale C5-C6, Conflit C6",
    "IRM poignet: Rupture ligament scapho-lunaire",
    "IRM cheville: Rupture tendon Achille, Diastasis 25mm",
    "IRM pelvis: Endométriose profonde, Nodules utéro-sacrés",
    "IRM sella: Microadénome hypophysaire 6mm",
    "IRM orbites: Névrite optique rétro-bulbaire gauche",
    "IRM fosse postérieure: Neurinome acoustique 18mm CPA",
    "Angio-IRM: Anévrisme communicante antérieure 7mm",
    "IRM abdominale: Pancréatite chronique, Atrophie",
    "IRM sein: BIRADS 2, Adénofibrome 15mm",
    "IRM hanche: Ostéonécrose tête fémorale stade II",
    "IRM coude: Epicondylite latérale",
    "IRM pied: Fasciite plantaire, Epaississement 6mm",
    "IRM main: Ténosynovite fléchisseurs, Canal carpien",
    "Cholangio-IRM: Lithiase vésiculaire, VBP 8mm",
    "Entéro-IRM: Maladie Crohn iléale",
    "IRM rectale: Cancer rectal T3N1",
    "Arthro-IRM épaule: Rupture transfixiante sus-épineux",
    "IRM rachis dorsal: Hémangiome D8",
    "IRM temporale: Otospongiose platine",
    "IRM thyroïde: Nodule 22mm TIRADS 4",
    "IRM surrénales: Adénome surrénale 28mm",
    "IRM médullaire: Sclérose en plaques, Hypersignaux T2",
    "IRM anorectale: Fistule inter-sphinctérienne",
    "IRM ATM: Luxation discale antérieure réductible",
    "IRM plexus brachial: Compression C8-D1, Pancoast"
]

prescriptions = [
    "ORDONNANCE: AMOXICILLINE 1g 1cp 3x/jour 7 jours. PARACETAMOL 1g si douleur",
    "Prescription: METFORMINE 850mg matin-soir. RAMIPRIL 5mg matin. ATORVASTATINE 20mg soir",
    "Rx: KARDEGIC 75mg matin. BISOPROLOL 5mg matin. FUROSEMIDE 40mg matin",
    "LEVOTHYROX 75µg matin jeun. CALCIUM+VIT-D3 1 sachet/jour",
    "VENTOLINE 100µg 2 bouffées 4x/jour. SERETIDE 250/25 matin-soir",
    "DOLIPRANE 1000mg 1cp/6h si fièvre. IBUPROFENE 400mg 3x/jour",
    "AUGMENTIN 1g 2x/jour 10 jours infection bronchique",
    "INEXIUM 40mg matin jeun. GAVISCON après repas",
    "SEROPLEX 10mg matin. Augmenter 20mg après 1 semaine",
    "TAHOR 20mg soir. Bilan lipidique 3 mois",
    "COVERSYL 5mg matin. AMLOR 5mg soir. Surveillance TA",
    "XARELTO 20mg/jour dîner. Consultation 3 mois",
    "SPASFON 80mg 3x/jour. SMECTA 1 sachet 3x/jour",
    "LOVENOX 0.4mL SC 1x/jour 10 jours post-op",
    "FORLAX 10g matin. Fibres. Hydratation",
    "LYRICA 75mg 2x/jour douleurs neuropathiques",
    "IMOVANE 7.5mg coucher insomnie. Max 4 semaines",
    "SPIRIVA 18µg matin BPCO. BRICANYL si dyspnée",
    "LORATADINE 10mg matin allergie. MOMETASONE spray nasal",
    "DAFLON 500mg 2cp matin-2cp midi. Contention",
    "LYSANXIA 10mg 3x/jour. Diminution 2 semaines",
    "EUPANTOL 20mg matin jeun reflux. 4 semaines",
    "MOPRAL 20mg matin jeun ulcère. 6 semaines",
    "CORTANCYL 20mg matin polyarthrite. Décroissance progressive",
    "IMUREL 50mg 2cp/jour. NFS mensuelle",
    "METHOTREXATE 15mg/semaine. SPECIAFOLDINE lendemain",
    "LAMALINE 1cp/6h douleurs. Max 8cp/jour",
    "TRAMADOL LP 100mg 2x/jour. DUROGÉSIC si échec",
    "OXYCONTIN 10mg 2x/jour cancer. OXYNORM inter-doses",
    "ZOPHREN 8mg 3x/jour nausées chimio",
    "KARDEGIC 160mg/jour syndrome coronarien. PLAVIX 75mg 1 an",
    "APROVEL 150mg matin HTA. TA <140/90",
    "MODOPAR 125mg 3x/jour Parkinson. Augmentation progressive",
    "ARICEPT 10mg soir Alzheimer. Suivi 6 mois",
    "SINGULAIR 10mg soir asthme. VENTOLINE secours"
]

medical_reports = [
    "COMPTE-RENDU HOSPITALISATION: Admission 12/03 dyspnée. Embolie pulmonaire. HBPM puis AVK. Sortie 18/03",
    "Rapport cardio: Angor stable II. ECG ondes T négatives. Echo FEVG 55%. Coronarographie indiquée",
    "CR opératoire: Cholécystectomie cœlio 15/03 AG. Clippage canal cystique. Suites simples",
    "Rapport anapath: Biopsie cutanée. Naevus composé sans atypie. Marges saines",
    "CR dermato: Lésion pigmentée 8mm asymétrique. Dermoscopie atypique. Exérèse programmée",
    "Synthèse: Infarctus antérieur. Angioplastie IVA stent. FEVG 45%. Réadaptation",
    "CR urgences: Traumatisme crânien léger. Glasgow 15. Scanner normal. Surveillance 24h",
    "Rapport gastro: Coloscopie. Polype sigmoïde 12mm réséqué. Adénome bas grade",
    "CR neuro: Céphalées migraineuses. 8 crises/mois. Traitement fond bêtabloquant",
    "Synthèse néphro: IRC stade 3. DFG 45. Néphroprotection IEC. Régime hypoprotidique",
    "CR psy: Episode dépressif sévère. Risque suicidaire. Hospitalisation. ISRS",
    "Rapport pneumo: BPCO stade III. VEMS 45%. Bronchodilatateurs. Sevrage tabac",
    "CR rhumato: Polyarthrite active. DAS28 5.8. Méthotrexate biothérapie",
    "Synthèse endoc: Diabète type 2 déséquilibré. HbA1c 8.5%. Complications débutantes",
    "CR ORL: Vertige positionnel. Dix-Hallpike positif. Manœuvre Epley. Résolution",
    "Rapport uro: HBP. IPSS 22/35. Prostate 60g. PSA 4.2. Alphabloquant",
    "CR gynéco: Ménopause 52 ans. Bouffées chaleur. THM oestrogènes progestérone",
    "Synthèse hémato: Anémie ferriprive. Hb 9.5. Fer effondré. Supplémentation",
    "CR ortho: PTH droite coxarthrose. Voie antérieure. Appui J1",
    "Rapport onco: Cancer sein T2N1M0. Stadification IIA. Chimiothérapie néoadjuvante",
    "CR médecine interne: Lupus systémique. Critères ACR+. Corticoïdes hydroxychloroquine",
    "Synthèse infectio: Pyélonéphrite E.coli. Bactériémie. C3G 14 jours",
    "CR gériatrie: Chute. Fracture col fémoral. Ostéosynthèse. Rééducation SSR",
    "Rapport pédiatrie: Bronchiolite 4 mois. Détresse respiratoire. Oxygénothérapie",
    "CR allergo: Allergie acariens pollens. Tests positifs. Désensibilisation",
    "Synthèse addictologie: Sevrage alcoolique. Syndrome sevrage. Détoxification",
    "CR chirurgie digestive: Appendicectomie. Appendice perforé. Lavage drainage",
    "Rapport vasculaire: Anévrisme aorte 55mm. EVAR. Surveillance annuelle",
    "CR médecine physique: AVC sylvien. Hémiplégie droite. Rééducation intensive",
    "Synthèse médecine travail: Lombalgie chronique. Inaptitude. Reclassement",
    "CR médecine légale: Coups blessures. ITT 8 jours. Certificat initial",
    "Rapport palliatif: Cancer pancréas métastatique. Soins confort. HAD",
    "CR génétique: Cancer sein précoce. Mutation BRCA1. Conseil famille",
    "Synthèse nutrition: Dénutrition sévère. Perte 15% 3 mois. Nutrition entérale",
    "CR médecine sport: Entorse cheville grade 2. Immobilisation 3 semaines. Rééducation"
]

lab_results = [
    "RESULTATS LABO: HbA1c 7.2%, Cholestérol 2.10 g/L, TSH 2.8 mUI/L, Créatinine 92 µmol/L",
    "Résultats bio: CRP 85 mg/L, VS 45 mm. NFS: Leucocytes 14000 polynucléose 85%",
    "Bilan thyroïdien: TSH 0.2 mUI/L, T3 7.2 pmol/L, T4 28 pmol/L, Anti-TPO 450 UI/mL",
    "Sérologie VIH négative. Hépatite B: Ag HBs négatif, Anti-HBs 250 UI/L vacciné",
    "ECBU: Leucocytes >10000, Nitrites+. Culture E.coli >100000. Sensible amox-clav",
    "Sérologie toxoplasmose: IgG positif 120 UI/mL, IgM négatif immunité ancienne",
    "Hémocultures: Staphylococcus aureus sensible méticilline. Antibiogramme complet",
    "PSA total 8.5 ng/mL, PSA libre 1.2, Ratio 14%. Biopsies prostate recommandées",
    "Marqueurs tumoraux: CEA 45 ng/mL, CA19-9 280 U/mL, CA125 normal",
    "Protéinurie 24h: 2.5 g/24h. Microalbuminurie 450 mg/L. Atteinte rénale",
    "Gazométrie artérielle: pH 7.35, PaCO2 48, PaO2 68, HCO3 26, Lactates 2.2",
    "Ponction lombaire: Liquide clair, Protéinorachie 0.35 g/L, Glycorachie normale",
    "Ionogramme urinaire: Natriurèse 85 mmol/24h, Kaliurèse 60 mmol/24h",
    "BNP 850 pg/mL insuffisance cardiaque décompensée",
    "D-dimères 2500 ng/mL. Suspicion thrombose. Angio-scanner à faire",
    "Procalcitonine 4.2 ng/mL sepsis. Antibiothérapie urgente",
    "Ferritine 850 ng/mL, CRP 125 mg/L. Syndrome inflammatoire",
    "Sérologie Lyme: IgM négatif, IgG positif. Western blot confirmatoire",
    "HIV-1 RNA charge virale indétectable <20 copies/mL. CD4 650/mm³",
    "AgHBs positif, ADN VHB 5 log, Hépatite B chronique active",
    "Anticorps anti-nucléaires 1/320 moucheté. Anticorps anti-DNA natifs positifs",
    "ANCA positifs PR3. Vascularite granulomateuse Wegener",
    "Facteur rhumatoïde 185 UI/mL, Anti-CCP 420 U/mL. Polyarthrite rhumatoïde",
    "Coombs direct positif. Anémie hémolytique auto-immune",
    "Myélogramme: Envahissement blastes 65%. Leucémie aiguë myéloïde",
    "Sperme: Oligospermie sévère 2 millions/mL. Asthénospermie 15% mobilité",
    "Test sueur: Chlore 85 mmol/L. Test positif mucoviscidose",
    "Cortisol libre urinaire 450 µg/24h. Syndrome Cushing",
    "Aldostérone 450 pg/mL, Rénine basse. Hyperaldostéronisme primaire Conn",
    "Homocystéine 35 µmol/L. Hyperhomocystéinémie risque cardiovasculaire",
    "Cryoglobulines positives type II. Purpura vascularite",
    "Complément CH50 effondré. Activation voie classique",
    "IgE totales 2500 UI/mL. Terrain atopique sévère",
    "Electrophorèse immunofixation: Pic monoclonal IgG kappa. Myélome multiple",
    "Calprotectine fécale 850 µg/g. MICI active Crohn ou RCH"
]

consultation_notes = [
    "NOTE CONSULTATION 17/03: Patient 45 ans lombalgies chroniques 6 mois. Recrudescence nocturne. Rachis raide. AINS kiné IRM",
    "Consultation diabéto 20/03: Diabète type 2 3 ans. HbA1c 6.8% stable. Glycémies 1.10-1.25. Metformine bien toléré. Revoir 3 mois",
    "CR pneumo: Dyspnée effort stade II. Spirométrie VEMS 68%. BPCO stade II. Arrêt tabac impératif. Bronchodilatateurs",
    "Note gynéco: Patiente 52 ans ménopause 2 ans. Bouffées chaleur invalidantes. Examen normal. THM oestrogènes progestérone",
    "Consultation pédiatrie: Nourrisson 6 mois 7.2kg 67cm PC 43cm. Développement normal. Vaccins jour. Diversification. Revoir 9 mois",
    "Note cardio: Patient 58 ans HTA non contrôlée. TA cabinet 165/95. Automesure 155/90. Bithérapie ARAII+TZD. Revoir 2 mois",
    "CR dermato: Patiente 35 ans acné sévère. Nombreux kystes nodules. Roaccutane 40mg/jour. Contraception obligatoire",
    "Consultation ORL: Enfant 6 ans otites récidivantes. 8 épisodes an. Examen tympans rétractés. Aérateurs transtympaniques",
    "Note ophtalmo: Diabétique 15 ans. Fond œil: Microanévrismes hémorragies. Rétinopathie non proliférante modérée. Surveillance 6 mois",
    "CR uro: Homme 68 ans dysurie nycturie. IPSS 18. Prostate 45g régulière. PSA 2.8. Alphabloquant tamsulosine",
    "Consultation rhumato: Femme 55 ans polyarthrite 2 ans. DAS28 3.2 rémission. Méthotrexate 15mg/semaine. Maintien traitement",
    "Note gastro: Patient 42 ans RGO pyrosis quotidien. Endoscopie œsophagite grade B. IPP double dose 8 semaines",
    "CR endocrino: Hypothyroïdie Hashimoto. TSH 8.5 sous Lévothyrox 75. Augmenter 100µg. Contrôle TSH 6 semaines",
    "Consultation allergologie: Enfant 8 ans rhinite asthme. Tests acariens pollens positifs. Corticoïdes inhalés éviction",
    "Note psychiatrie: Adulte 28 ans anxiété généralisée. Attaques panique 2-3/semaine. ISRS escitalopram 10mg TCC",
    "CR néphrologie: IRC stade 3b DFG 38. TA 145/85. Protéinurie 1.2g. Renforcer néphroprotection. Prévoir FAV",
    "Consultation hématologie: Anémie microcytaire Hb 10.2 VGM 72. Ferritine 12. Coloscopie recherche saignement. Fer IV",
    "Note infectio: Fièvre 5 jours pneumopathie. Amoxicilline 48h sans amélioration. Hospitalisation C3G IV",
    "CR gériatrie: 82 ans chutes répétées. 3 derniers mois. Hypotension orthostatique. Revoir traitement. Kiné équilibre",
    "Consultation addictologie: Sevrage tabac 25 PA. Motivation 8/10. Substituts nicotiniques varéniciline. Suivi hebdomadaire",
    "Note médecine sport: Sportif marathon entorse cheville 3 semaines. Examen stable. Reprise progressive course 2 semaines",
    "CR nutrition: Obésité morbide IMC 42. Chirurgie bariatrique envisagée. Bilan préopératoire. RCP pluridisciplinaire",
    "Consultation douleur: Lombo-radiculalgie chronique. EVA 7/10. Morphiniques inefficaces. Infiltration épidurale programmée",
    "Note médecine travail: Salarié BTP lombalgie. Port charges lourdes. Restriction aptitude. Aménagement poste",
    "CR soins palliatifs: Cancer poumon stade IV. ECOG 3. Dyspnée morphine oxygène. HAD mise place",
    "Consultation génétique: Antécédent familial cancer sein mère tante. Test BRCA négatif. Surveillance standard",
    "Note planning familial: Contraception 25 ans. Pilule oublis fréquents. Implant sous-cutané posé",
    "CR MPR: Post-AVC 3 mois. Récupération motrice partielle. Poursuite rééducation intensive. Bilan 3 mois",
    "Consultation voyage: Séjour Afrique 3 semaines. Vaccins fièvre jaune hépatite A. Chimioprophylaxie paludisme",
    "Note médecine légale: Victime agression. Ecchymoses multiples. ITT 5 jours. Certificat remis mains propres",
    "CR tabacologie: Fumeur 30 cigarettes/jour 20 ans. Tentatives sevrage 3 échecs. Varéniciline substituts. Suivi",
    "Consultation mémoire: Troubles cognitifs 2 ans. MMS 22/30. IRM atrophie hippocampes. Alzheimer débutant",
    "Note sommeil: Insomnie chronique. Latence 2h réveils multiples. Hygiène sommeil TCC. Zolpidem court terme",
    "CR infectio pédo: Varicelle compliquée surinfection. Hospitalisation aciclovir antibiotiques. Evolution favorable",
    "Consultation préanesthésie: ASA 2. Intubation prévue. Bilan complet normal. Prémédication anxiolytique"
]

# Combine all data
for text in blood_tests:
    data.append([text, 'blood_test'])
for text in xrays:
    data.append([text, 'xray'])
for text in mris:
    data.append([text, 'mri'])
for text in prescriptions:
    data.append([text, 'prescription'])
for text in medical_reports:
    data.append([text, 'medical_report'])
for text in lab_results:
    data.append([text, 'lab_result'])
for text in consultation_notes:
    data.append([text, 'consultation_note'])

# Write to CSV
with open('training_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['text', 'label'])
    writer.writerows(data)

print(f"✅ Created training_data.csv")
print(f"   Total samples: {len(data)}")
print(f"   blood_test: {len(blood_tests)}")
print(f"   xray: {len(xrays)}")
print(f"   mri: {len(mris)}")
print(f"   prescription: {len(prescriptions)}")
print(f"   medical_report: {len(medical_reports)}")
print(f"   lab_result: {len(lab_results)}")
print(f"   consultation_note: {len(consultation_notes)}")
print(f"\n📤 Upload this file to Google Colab and retrain!")
