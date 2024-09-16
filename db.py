from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base, Session
import click

from flask import url_for
from flask import current_app as app

import os, sqlite3

if os.path.isdir('apprimatologia'):
    database_path = os.path.join('instance', 'apprimatologia.db')
else:
    database_path = 'apprimatologia.db'

conn = sqlite3.connect(database_path)
conn.close()

engine = create_engine('sqlite:///' + database_path)
_db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = _db_session.query_property()

def get_session() -> Session:
    return Session(bind=engine)


@click.command('init-db')
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    
    from . import models
    from .files import models as file_models
    Base.metadata.create_all(bind=engine)

    with get_session() as db_session:
        # missing_photo = file_models.UploadedFile(
        #     original_name = 'MissingAvatar.png',
        #     file_path=os.path.join(app.root_path, 'static', 'img', 'MissingAvatar.png')
        # )
        # db_session.add(missing_photo)


        # # Tania Minhos
        # photo = file_models.UploadedFile(
        #     original_name = 'TaniaMinhos.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'TaniaMinhos.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Tânia Minhós', 
        #     description_pt='Tânia Minhós is a Professor at the School of Social Sciences and Humanities of Universidade Nova de Lisboa (NOVA FCSH) since 2015 at the Anthropology department. She has conducted research in West Africa since 2008, focusing on sympatric primate species with different socio-ecologies to address questions related to their adaptive strategies to the human-led changes in their environments, namely the impacts and drivers of deforestation and hunting.  Recognizing the multi-layer dimensions of these challenges, Tânia’s research combines cross-disciplinary data (e.g. genetics, ecology, behavior, social), to address questions related to evolution and adaptation of non-human primates inhabiting anthropogenic habitats and to gain insights on the human-nonhuman primate interactions in fast-changing environments. The ultimate goal of her research is to bring local communities, conservation practitioners, and researchers together to develop strategies aiming at the sustainable coexistence of human communities and nonhuman primates in shared landscapes.', 
        #     description_en='Tânia Minhós is a Professor at the School of Social Sciences and Humanities of Universidade Nova de Lisboa (NOVA FCSH) since 2015 at the Anthropology department. She has conducted research in West Africa since 2008, focusing on sympatric primate species with different socio-ecologies to address questions related to their adaptive strategies to the human-led changes in their environments, namely the impacts and drivers of deforestation and hunting.  Recognizing the multi-layer dimensions of these challenges, Tânia’s research combines cross-disciplinary data (e.g. genetics, ecology, behavior, social), to address questions related to evolution and adaptation of non-human primates inhabiting anthropogenic habitats and to gain insights on the human-nonhuman primate interactions in fast-changing environments. The ultimate goal of her research is to bring local communities, conservation practitioners, and researchers together to develop strategies aiming at the sustainable coexistence of human communities and nonhuman primates in shared landscapes.',
        #     direction=1,
        #     direction_order=1,
        #     position_pt='Presidente',
        #     position_en='President',
        #     photo=photo.id,
        #     orcid='0000-0003-0183-1343'
        # )
        # db_session.add(profile)


        # # Maria Joana Silva
        # photo = file_models.UploadedFile(
        #     original_name = 'MariaJoanaSilva.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'MariaJoanaSilva.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Maria Joana Silva', 
        #     description_pt='Dr. Maria Joana Ferreira da Silva, Ph.D. in Biosciences since 2012, is an FCT associated researcher in BIOPOLIS/CIBIO (CEECIND/01937/2017, 2019-2025). Before, she was an FCT-funded postdoctoral researcher (2013-2019, five months interruption for maternity leave). Her main research areas are Biological Anthropology and Conservation Biology. She investigates the relationship between human and African non-human primates and the impacts of anthropogenic activities on the distribution, socio-ecology, and conservation. The overarching goal is to improve management of threatened taxa in developing countries. She has been investigating African (threatened) primates in Guinea-Bissau, Tanzania, Mauritania, and Mozambique, using inter-disciplinary methods - ethnography, population genetics and genomics, and spatial ecology. She has published on themes such as biological anthropology, population and conservation genetics/genomics, perceptions on non-human primates, illegal wildlife trafficking, behavioural adaptations and human evolution. She is currently the PI of a project aiming to understand the illegal trade of primate meat in bars and restaurants in Guinea-Bissau, West Africa.', 
        #     description_en='Dr. Maria Joana Ferreira da Silva, Ph.D. in Biosciences since 2012, is an FCT associated researcher in BIOPOLIS/CIBIO (CEECIND/01937/2017, 2019-2025). Before, she was an FCT-funded postdoctoral researcher (2013-2019, five months interruption for maternity leave). Her main research areas are Biological Anthropology and Conservation Biology. She investigates the relationship between human and African non-human primates and the impacts of anthropogenic activities on the distribution, socio-ecology, and conservation. The overarching goal is to improve management of threatened taxa in developing countries. She has been investigating African (threatened) primates in Guinea-Bissau, Tanzania, Mauritania, and Mozambique, using inter-disciplinary methods - ethnography, population genetics and genomics, and spatial ecology. She has published on themes such as biological anthropology, population and conservation genetics/genomics, perceptions on non-human primates, illegal wildlife trafficking, behavioural adaptations and human evolution. She is currently the PI of a project aiming to understand the illegal trade of primate meat in bars and restaurants in Guinea-Bissau, West Africa.',
        #     direction=1,
        #     direction_order=2,
        #     position_pt='Vice-presidente',
        #     position_en='Vice-president',
        #     photo=photo.id,
        #     website='https://www.cienciavitae.pt/portal/A71C-1675-4ECC',
        #     orcid='0000-0001-6747-9827'
        # )
        # db_session.add(profile)


        # # Ivo Colmonero Costeira
        # photo = file_models.UploadedFile(
        #     original_name = 'IvoColmoneroCosteira.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'IvoColmoneroCosteira.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Ivo Colmonero Costeira', 
        #     description_pt="Ivo Colmonero Costeira is a PhD student at Cardiff University, UK, and a research collaborator at the University of Porto and the University of Coimbra, Portugal.  He has been working since 2017 on the conservation of guenons (tribe Cercopithecini) in West Africa, and for his PhD he has been investigating how the socio-cultural importance of non-human primate species changed throughout history and it's link to current population structure, genetic diversity and past fluctuations of effective population size. His work requires the combined use of of genetic/genomic and ethnographic tools.", 
        #     description_en="Ivo Colmonero Costeira is a PhD student at Cardiff University, UK, and a research collaborator at the University of Porto and the University of Coimbra, Portugal.  He has been working since 2017 on the conservation of guenons (tribe Cercopithecini) in West Africa, and for his PhD he has been investigating how the socio-cultural importance of non-human primate species changed throughout history and it's link to current population structure, genetic diversity and past fluctuations of effective population size. His work requires the combined use of of genetic/genomic and ethnographic tools.",
        #     direction=1,
        #     direction_order=3,
        #     position_pt='Secretário',
        #     position_en='Secretary',
        #     photo=photo.id,
        #     orcid='0000-0001-9914-0713'
        # )
        # db_session.add(profile)


        # # Susana Costa
        # photo = file_models.UploadedFile(
        #     original_name = 'SusanaCosta.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'SusanaCosta.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Susana Costa', 
        #     description_pt='Doutorada em Psicologia pela Universidade de Stirling (Escola de Ciências Naturais), Escócia, Reino Unido. É atualmente investigadora do CIAS - Centro de Investigação em Antropologia e Saúde (Departamento de Ciências da Vida, Universidade de Coimbra). Os seus interesses de pesquisa são as percepções humanas sobre outras espécies animais e a biodiversidade em geral e como elas podem interferir nos esforços de conservação ambiental. Tem experiência de campo em África - em particular na Guiné-Bissau - e conhecimentos em análise quantitativa e qualitativa de dados. Conta com várias publicações sobre as relações humanos/outros animais e colabora regularmente com o Programa de Pós-Graduação em Estudos da Cultura Contemporânea da Universidade Federal de Mato Grosso (Brasil). Exerce atividades de docência com regularidade em diversas instituições de ensino superior públicas e privadas.', 
        #     description_en='Doutorada em Psicologia pela Universidade de Stirling (Escola de Ciências Naturais), Escócia, Reino Unido. É atualmente investigadora do CIAS - Centro de Investigação em Antropologia e Saúde (Departamento de Ciências da Vida, Universidade de Coimbra). Os seus interesses de pesquisa são as percepções humanas sobre outras espécies animais e a biodiversidade em geral e como elas podem interferir nos esforços de conservação ambiental. Tem experiência de campo em África - em particular na Guiné-Bissau - e conhecimentos em análise quantitativa e qualitativa de dados. Conta com várias publicações sobre as relações humanos/outros animais e colabora regularmente com o Programa de Pós-Graduação em Estudos da Cultura Contemporânea da Universidade Federal de Mato Grosso (Brasil). Exerce atividades de docência com regularidade em diversas instituições de ensino superior públicas e privadas.',
        #     direction=1,
        #     direction_order=4,
        #     position_pt='Tesoureira',
        #     position_en='Treasurer',
        #     photo=photo.id,
        #     orcid='0000-0002-2766-0135'
        # )
        # db_session.add(profile)


        # # Catarina Casanova
        # photo = file_models.UploadedFile(
        #     original_name = 'CatarinaCasanova.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'CatarinaCasanova.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Catarina Casanova',
        #     description_pt='Prof. Catarina Casanova got her PhD from the University of Cambridge (UK) under the supervision of Prof. Phyllis Lee in Biological Anthropology (and got her undergrad and master anthropology diplomas from the University of Lisbon). Currently she is associate professor (tenure track) at the University of Lisbon (School of Social and Political Sciences/ISCSP). Her research areas are both in Cultural and Biological Anthropology. In Cultural Anthropology she works in multi-species anthropology/environmental anthropology. Her work in Biological anthropology is mainly focus on Primatology (chimpanzees and other primates of Guinea Bissau, mona monkeys from São Tomé & Príncipe and other nonhuman primates - in captivity enclosures and in Brazil - studying social behaviour, conservation, local communities and their relationship with nonhuman primate communities (conflicts, local knowledge, amongst other topics) and evolution. C. Casanova supervised and/or co-supervised 8 PhD thesis (concluded mostly with FCT funding) and she is currently supervising or co-supervising 2 PhD students (both with FCT funding). She already supervised (and/or co-supervised) more than 40 MSc dissertations (concluded) and is currently supervising (and/or co-supervising) 2 MSc students. She is currently supervising her 8th post-doc researcher. C. Casanova is a full researcher at CIAS (Centro de Investigação em Antropologia e Saúde), University of Coimbra and she is a collaborator of CAPP (ISCSP). She published 4 books and co-edited 1 book. She has more than 60 publications (most of them with peer review systems; research articles and book chapters).', 
        #     description_en='Prof. Catarina Casanova got her PhD from the University of Cambridge (UK) under the supervision of Prof. Phyllis Lee in Biological Anthropology (and got her undergrad and master anthropology diplomas from the University of Lisbon). Currently she is associate professor (tenure track) at the University of Lisbon (School of Social and Political Sciences/ISCSP). Her research areas are both in Cultural and Biological Anthropology. In Cultural Anthropology she works in multi-species anthropology/environmental anthropology. Her work in Biological anthropology is mainly focus on Primatology (chimpanzees and other primates of Guinea Bissau, mona monkeys from São Tomé & Príncipe and other nonhuman primates - in captivity enclosures and in Brazil - studying social behaviour, conservation, local communities and their relationship with nonhuman primate communities (conflicts, local knowledge, amongst other topics) and evolution. C. Casanova supervised and/or co-supervised 8 PhD thesis (concluded mostly with FCT funding) and she is currently supervising or co-supervising 2 PhD students (both with FCT funding). She already supervised (and/or co-supervised) more than 40 MSc dissertations (concluded) and is currently supervising (and/or co-supervising) 2 MSc students. She is currently supervising her 8th post-doc researcher. C. Casanova is a full researcher at CIAS (Centro de Investigação em Antropologia e Saúde), University of Coimbra and she is a collaborator of CAPP (ISCSP). She published 4 books and co-edited 1 book. She has more than 60 publications (most of them with peer review systems; research articles and book chapters).',
        #     direction=1,
        #     direction_order=5,
        #     position_pt='Vogal',
        #     position_en='',
        #     photo=photo.id,
        #     orcid='0000-0003-2123-0262'
        # )
        # db_session.add(profile)


        # # Cecilia Veracini
        # # photo = file_models.UploadedFile(
        # #     original_name = 'CeciliaVeracini.jpg',
        # #     file_path=os.path.join(app.root_path, '..', 'content', 'CeciliaVeracini.jpg')
        # # )
        # # db_session.add(photo)

        # profile = models.Profile(
        #     name='Cecilia Veracini',
        #     description_pt='', 
        #     description_en='',
        #     direction=True,
        #     direction_order=6,
        #     position_pt='Vogal',
        #     position_en='',
        #     photo=missing_photo.id,
        #     orcid=''
        # )
        # db_session.add(profile)


        # # Isa Aleixo Pais
        # photo = file_models.UploadedFile(
        #     original_name = 'IsaAleixoPais.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'IsaAleixoPais.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Isa Aleixo-Pais', 
        #     description_pt='Isa Aleixo-Pais é pós-doutoranda no Centro de Investigação de Montanha no Instituto Politécnico de Bragança, onde desenvolve trabalho com a comunidade pastoril a fim de determinar adaptações às alterações climáticas. Em 2023 concluiu o doutoramento em Antropologia Biológica e Biologia da Conservação pela Universidade de Cardiff, País de Gales, em colaboração com o Centro em Rede de Investigação em Antropologia (CRIA-NOVA FCSH/IN2PAST). Desde 2010 que integra equipas de investigação e conservação de primatas não-humanos em Madagáscar e África Ocidental. A sua investigação combina técnicas de biologia molecular (ex. DNA metabarcoding) e antropologia com o objectivo de estudar sistemas socio-ecológicos em que humanos e animais não-humanos co-habitam e partilham recursos naturais.', 
        #     description_en='Isa Aleixo-Pais é pós-doutoranda no Centro de Investigação de Montanha no Instituto Politécnico de Bragança, onde desenvolve trabalho com a comunidade pastoril a fim de determinar adaptações às alterações climáticas. Em 2023 concluiu o doutoramento em Antropologia Biológica e Biologia da Conservação pela Universidade de Cardiff, País de Gales, em colaboração com o Centro em Rede de Investigação em Antropologia (CRIA-NOVA FCSH/IN2PAST). Desde 2010 que integra equipas de investigação e conservação de primatas não-humanos em Madagáscar e África Ocidental. A sua investigação combina técnicas de biologia molecular (ex. DNA metabarcoding) e antropologia com o objectivo de estudar sistemas socio-ecológicos em que humanos e animais não-humanos co-habitam e partilham recursos naturais.',
        #     direction=1,
        #     direction_order=7,
        #     position_pt='Vogal',
        #     position_en='',
        #     photo=photo.id,
        #     website='https://www.cienciavitae.pt/portal/en/3B1F-4EA6-5719',
        #     orcid='0000-0003-2730-3688'
        # )
        # db_session.add(profile)


        # # Joana Roque Pinho
        # photo = file_models.UploadedFile(
        #     original_name = 'JoanaRoquePinho.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'JoanaRoquePinho.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Joana Roque Pinho', 
        #     description_pt='Joana Roque de Pinho is an ecologist and environmental anthropologist whose research focuses on changing West and East African sub-humid and dryland social-ecological systems; and how members of rural natural-resource reliant communities experience and understand environmental changes. She is most passionate about collaborating directly with rural community members as collaborative researchers/visual ethnographers through participatory visual research methodologies. For the MYNA project, she explores the intersection of religious transformations with livelihoods, land tenure/use changes and climatic instability. She contributes a multi-sited Kenyan case-study that explores the neglected role of Christianity in Maasailand’s social-ecological dynamics, and participates in the Mongolia and Mozambique case studies.', 
        #     description_en='Joana Roque de Pinho is an ecologist and environmental anthropologist whose research focuses on changing West and East African sub-humid and dryland social-ecological systems; and how members of rural natural-resource reliant communities experience and understand environmental changes. She is most passionate about collaborating directly with rural community members as collaborative researchers/visual ethnographers through participatory visual research methodologies. For the MYNA project, she explores the intersection of religious transformations with livelihoods, land tenure/use changes and climatic instability. She contributes a multi-sited Kenyan case-study that explores the neglected role of Christianity in Maasailand’s social-ecological dynamics, and participates in the Mongolia and Mozambique case studies.',
        #     direction=2,
        #     direction_order=1,
        #     position_pt='Presidente',
        #     position_en='President',
        #     photo=photo.id,
        #     orcid='0000-0002-4659-2684'
        # )
        # db_session.add(profile)


        # # # Fátima Almeida 
        # # photo = file_models.UploadedFile(
        # #     original_name = 'FátimaAlmeida.jpg',
        # #     file_path=os.path.join(app.root_path, '..', 'content', 'FátimaAlmeida.jpg')
        # # )
        # # db_session.add(photo)

        # profile = models.Profile(
        #     name='Fátima Almeida', 
        #     description_pt='', 
        #     description_en='',
        #     direction=2,
        #     direction_order=2,
        #     position_pt='Secretária',
        #     position_en='Secretary',
        #     photo=missing_photo.id,
        #     orcid=''
        # )
        # db_session.add(profile)


        # # Filipa Borges
        # photo = file_models.UploadedFile(
        #     original_name = 'FilipaBorges.jpg',
        #     file_path=os.path.join(app.root_path, '..', 'content', 'FilipaBorges.jpg')
        # )
        # db_session.add(photo)

        # profile = models.Profile(
        #     name='Filipa Borges', 
        #     description_pt='Filipa Borges é estudante de doutoramento em Antropologia afiliada ao Centro em Rede de Investigação em Antropologia (CRIA-NOVA FCSH/IN2PAST), à Universidade de Exeter e à Universidade do Porto. O seu trabalho combina técnicas de genómica e de ciência social para estudar a interface entre primatas não-humanos e humanos na África Ocidental, principalmente na Serra Leoa.', 
        #     description_en='Filipa Borges is a PhD candidate in Anthropology affiliated with the Centre for Research in Anthropology (CRIA-NOVA FCSH/IN2PAST), the University of Exeter, and the University of Porto. Her work integrates genomics and social sciences methods to study the human/nonhuman primate interface in West Africa, particularly Sierra Leone.',
        #     direction=2,
        #     direction_order=3,
        #     position_pt='Secretária',
        #     position_en='Secretary',
        #     photo=photo.id,
        #     orcid='0000-0002-1405-2341'
        # )
        # db_session.add(profile)


        # # Gonçalo Jesus
        # # photo = file_models.UploadedFile(
        # #     original_name = 'GonçaloJesus.jpg',
        # #     file_path=os.path.join(app.root_path, '..', 'content', 'GonçaloJesus.jpg')
        # # )
        # # db_session.add(photo)

        # profile = models.Profile(
        #     name='Gonçalo Jesus', 
        #     description_pt='', 
        #     description_en='',
        #     direction=3,
        #     direction_order=1,
        #     position_pt='Presidente',
        #     position_en='President',
        #     photo=missing_photo.id,
        #     orcid=''
        # )
        # db_session.add(profile)


        # # # Filipa Soares
        # # photo = file_models.UploadedFile(
        # #     original_name = 'FilipaSoares.jpg',
        # #     file_path=os.path.join(app.root_path, '..', 'content', 'FilipaSoares.jpg')
        # # )
        # # db_session.add(photo)

        # profile = models.Profile(
        #     name='Filipa Soares', 
        #     description_pt='', 
        #     description_en='',
        #     direction=3,
        #     direction_order=2,
        #     position_pt='Relatora',
        #     position_en='',
        #     photo=missing_photo.id,
        #     orcid=''
        # )
        # db_session.add(profile)


        # # Rui Moutinho Sá
        # # photo = file_models.UploadedFile(
        # #     original_name = 'RuiMoutinhoSá.jpg',
        # #     file_path=os.path.join(app.root_path, '..', 'content', 'RuiMoutinhoSá.jpg')
        # # )
        # # db_session.add(photo)

        # profile = models.Profile(
        #     name='Rui Moutinho Sá', 
        #     description_pt='', 
        #     description_en='',
        #     direction=3,
        #     direction_order=3,
        #     position_pt='Relator',
        #     position_en='',
        #     photo=missing_photo.id,
        #     orcid=''
        # )
        # db_session.add(profile)

        # # News
        # image_file = file_models.UploadedFile(
        #     original_name='IPC_Text Black_Logo.png',
        #     file_path=os.path.join(app.root_path, 'static', 'img', 'IPC_Text Black_Logo.png')
        # )
        # db_session.add(image_file)

        # image = models.Image(
        #      image_file.id,
        #      subtitle_pt='IX Conferência Ibéria de Primatologia (Vila do Conde, 21 a 23 de Novembro 2024)', 
        #      subtitle_en='IX Iberian Primatological Conference (Vila do Conde, November 21-23 2024)', 
        #      alt_pt=None, 
        #      alt_en=None
        # )
        # db_session.add(image)
        # db_session.commit()

        # news = models.News(
        #     title_pt = 'IX Congresso Ibérico de Primatologia', 
        #     title_en = 'IX Iberian Primatological Conference', 
        #     body_pt  = ''
        #       '<p>'
        #       '  É com enorme prazer que as Associações de Primatologia Portuguesa e Espanhola (APP e APE) anunciam o IX Congresso Ibérico de Primatologia, que terá lugar em Novembro de 2024 em Vila do Conde, Portugal, com o tema Beyond Boundaries: Integrating Primate Research. '
        #       '  Comunicações das diferentes áreas que integram a primatologia são bem-vindas e encorajamos todos os investigadores, independentemente da fase de carreira em que se encontrem, a submeterem um resumo. O prazo para submissão de resumos é 15 de Agosto. '
        #       "  Visita, por favor, o <a class='white-link' href='/IX_Iberian_Primatological_Conference/pt'>site do congresso</a> para saberes mais detalhes e te registares. E fica à vontade para nos contactares caso surja alguma dúvida. "
        #       '</p>'
        #       '<p>'
        #       '  Esperamos ver-te em breve!'
        #       '</p>'
        #     '', 
        #     body_en  =  ''
        #       '<p>'
        #       '  The Portuguese and Spanish Primatological Associations (APP and APE) are thrilled to announce the IX Iberian Primatological Conference, which will take place in November 2024 in Vila do Conde, Portugal, with the theme Beyond Boundaries: Integrating Primate Research. '
        #       '  We welcome communications from all fields of primatology and encourage researchers at all career stages to submit an abstract. Abstract submission closes on August 15th. '
        #       "  Please visit the <a class='white-link' href='/IX_Iberian_Primatological_Conference/en'>conference website</a> for details and registration, and do not hesitate to contact us if you have any questions. "
        #       '</p>'
        #       '<p>'
        #       '  We look forward to meeting you soon!'
        #       '</p>'
        #     '',
        #     image    = image.id
        # )
        # db_session.add(news)

        # news = models.News(
        #     title_pt = 'Novas datas!', 
        #     title_en = 'New dates!', 
        #     body_pt  = ''
        #       '<p>'
        #       '  Estendemos o prazo para submissão de resumos para o IX Congresso Ibérico de Primatologia até 15 de Setembro.'
        #       '</p>'
        #       '<p>'
        #       '  Aproveita! Até breve.'
        #       '</p>'
        #     '', 
        #     body_en  =  ''
        #       '<p>'
        #       '  We have extended the deadline for abstract submissions for the IX Iberian Primatological Conference to September 15th.'
        #       '</p>'
        #       '<p>'
        #       '  Take advantage of this opportunity! See you soon.'
        #       '</p>'
        #     ''
        # )
        # db_session.add(news)

        db_session.commit()

    click.echo('Initialized the database.')
