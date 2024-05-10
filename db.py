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
        # Catarina Casanova
        photo = file_models.UploadedFile(
            original_name = 'CatarinaCasanova.jpg',
            file_path=os.path.join(app.root_path, '..', 'content', 'CatarinaCasanova.jpg')
        )
        db_session.add(photo)

        profile = models.Profile(
            name='Catarina Casanova',
            description_pt='Prof. Catarina Casanova got her PhD from the University of Cambridge (UK) under the supervision of Prof. Phyllis Lee in Biological Anthropology (and got her undergrad and master anthropology diplomas from the University of Lisbon). Currently she is associate professor (tenure track) at the University of Lisbon (School of Social and Political Sciences/ISCSP). Her research areas are both in Cultural and Biological Anthropology. In Cultural Anthropology she works in multi-species anthropology/environmental anthropology. Her work in Biological anthropology is mainly focus on Primatology (chimpanzees and other primates of Guinea Bissau, mona monkeys from São Tomé & Príncipe and other nonhuman primates - in captivity enclosures and in Brazil - studying social behaviour, conservation, local communities and their relationship with nonhuman primate communities (conflicts, local knowledge, amongst other topics) and evolution. C. Casanova supervised and/or co-supervised 8 PhD thesis (concluded mostly with FCT funding) and she is currently supervising or co-supervising 2 PhD students (both with FCT funding). She already supervised (and/or co-supervised) more than 40 MSc dissertations (concluded) and is currently supervising (and/or co-supervising) 2 MSc students. She is currently supervising her 8th post-doc researcher. C. Casanova is a full researcher at CIAS (Centro de Investigação em Antropologia e Saúde), University of Coimbra and she is a collaborator of CAPP (ISCSP). She published 4 books and co-edited 1 book. She has more than 60 publications (most of them with peer review systems; research articles and book chapters).', 
            description_en='Prof. Catarina Casanova got her PhD from the University of Cambridge (UK) under the supervision of Prof. Phyllis Lee in Biological Anthropology (and got her undergrad and master anthropology diplomas from the University of Lisbon). Currently she is associate professor (tenure track) at the University of Lisbon (School of Social and Political Sciences/ISCSP). Her research areas are both in Cultural and Biological Anthropology. In Cultural Anthropology she works in multi-species anthropology/environmental anthropology. Her work in Biological anthropology is mainly focus on Primatology (chimpanzees and other primates of Guinea Bissau, mona monkeys from São Tomé & Príncipe and other nonhuman primates - in captivity enclosures and in Brazil - studying social behaviour, conservation, local communities and their relationship with nonhuman primate communities (conflicts, local knowledge, amongst other topics) and evolution. C. Casanova supervised and/or co-supervised 8 PhD thesis (concluded mostly with FCT funding) and she is currently supervising or co-supervising 2 PhD students (both with FCT funding). She already supervised (and/or co-supervised) more than 40 MSc dissertations (concluded) and is currently supervising (and/or co-supervising) 2 MSc students. She is currently supervising her 8th post-doc researcher. C. Casanova is a full researcher at CIAS (Centro de Investigação em Antropologia e Saúde), University of Coimbra and she is a collaborator of CAPP (ISCSP). She published 4 books and co-edited 1 book. She has more than 60 publications (most of them with peer review systems; research articles and book chapters).',
            direction=True,
            position_pt='Vice-Presidente',
            position_en='Vice-President',
            photo=photo.id,
            orcid='0000-0003-2123-0262'
        )
        db_session.add(profile)


        # Joana Roque Pinho
        photo = file_models.UploadedFile(
            original_name = 'JoanaRoquePinho.jpg',
            file_path=os.path.join(app.root_path, '..', 'content', 'JoanaRoquePinho.jpg')
        )
        db_session.add(photo)

        profile = models.Profile(
            name='Joana Roque Pinho', 
            description_pt='Joana Roque de Pinho is an ecologist and environmental anthropologist whose research focuses on changing West and East African sub-humid and dryland social-ecological systems; and how members of rural natural-resource reliant communities experience and understand environmental changes. She is most passionate about collaborating directly with rural community members as collaborative researchers/visual ethnographers through participatory visual research methodologies. For the MYNA project, she explores the intersection of religious transformations with livelihoods, land tenure/use changes and climatic instability. She contributes a multi-sited Kenyan case-study that explores the neglected role of Christianity in Maasailand’s social-ecological dynamics, and participates in the Mongolia and Mozambique case studies.', 
            description_en='Joana Roque de Pinho is an ecologist and environmental anthropologist whose research focuses on changing West and East African sub-humid and dryland social-ecological systems; and how members of rural natural-resource reliant communities experience and understand environmental changes. She is most passionate about collaborating directly with rural community members as collaborative researchers/visual ethnographers through participatory visual research methodologies. For the MYNA project, she explores the intersection of religious transformations with livelihoods, land tenure/use changes and climatic instability. She contributes a multi-sited Kenyan case-study that explores the neglected role of Christianity in Maasailand’s social-ecological dynamics, and participates in the Mongolia and Mozambique case studies.',
            direction=True,
            position_pt='Vogal',
            position_en='Vogal',
            photo=photo.id,
            orcid='0000-0002-4659-2684'
        )
        db_session.add(profile)


        # Maria Joana Silva
        photo = file_models.UploadedFile(
            original_name = 'MariaJoanaSilva.jpg',
            file_path=os.path.join(app.root_path, '..', 'content', 'MariaJoanaSilva.jpg')
        )
        db_session.add(photo)

        profile = models.Profile(
            name='Maria Joana Silva', 
            description_pt='Dr. Maria Joana Ferreira da Silva, Ph.D. in Biosciences since 2012, is an FCT associated researcher in BIOPOLIS/CIBIO (CEECIND/01937/2017, 2019-2025). Before, she was an FCT-funded postdoctoral researcher (2013-2019, five months interruption for maternity leave). Her main research areas are Biological Anthropology and Conservation Biology. She investigates the relationship between human and African non-human primates and the impacts of anthropogenic activities on the distribution, socio-ecology, and conservation. The overarching goal is to improve management of threatened taxa in developing countries. She has been investigating African (threatened) primates in Guinea-Bissau, Tanzania, Mauritania, and Mozambique, using inter-disciplinary methods - ethnography, population genetics and genomics, and spatial ecology. She has published on themes such as biological anthropology, population and conservation genetics/genomics, perceptions on non-human primates, illegal wildlife trafficking, behavioural adaptations and human evolution. She is currently the PI of a project aiming to understand the illegal trade of primate meat in bars and restaurants in Guinea-Bissau, West Africa.', 
            description_en='Dr. Maria Joana Ferreira da Silva, Ph.D. in Biosciences since 2012, is an FCT associated researcher in BIOPOLIS/CIBIO (CEECIND/01937/2017, 2019-2025). Before, she was an FCT-funded postdoctoral researcher (2013-2019, five months interruption for maternity leave). Her main research areas are Biological Anthropology and Conservation Biology. She investigates the relationship between human and African non-human primates and the impacts of anthropogenic activities on the distribution, socio-ecology, and conservation. The overarching goal is to improve management of threatened taxa in developing countries. She has been investigating African (threatened) primates in Guinea-Bissau, Tanzania, Mauritania, and Mozambique, using inter-disciplinary methods - ethnography, population genetics and genomics, and spatial ecology. She has published on themes such as biological anthropology, population and conservation genetics/genomics, perceptions on non-human primates, illegal wildlife trafficking, behavioural adaptations and human evolution. She is currently the PI of a project aiming to understand the illegal trade of primate meat in bars and restaurants in Guinea-Bissau, West Africa.',
            direction=True,
            position_pt='Presidente da Mesa da Assembleia',
            position_en='Presidente da Mesa da Assembleia',
            photo=photo.id,
            website='https://www.cienciavitae.pt/portal/A71C-1675-4ECC',
            orcid='0000-0001-6747-9827'
        )
        db_session.add(profile)


        # Susana Costa
        photo = file_models.UploadedFile(
            original_name = 'SusanaCosta.jpg',
            file_path=os.path.join(app.root_path, '..', 'content', 'SusanaCosta.jpg')
        )
        db_session.add(photo)

        profile = models.Profile(
            name='Susana Costa', 
            description_pt='Doutorada em Psicologia pela Universidade de Stirling (Escola de Ciências Naturais), Escócia, Reino Unido. É atualmente investigadora do CIAS - Centro de Investigação em Antropologia e Saúde (Departamento de Ciências da Vida, Universidade de Coimbra). Os seus interesses de pesquisa são as percepções humanas sobre outras espécies animais e a biodiversidade em geral e como elas podem interferir nos esforços de conservação ambiental. Tem experiência de campo em África - em particular na Guiné-Bissau - e conhecimentos em análise quantitativa e qualitativa de dados. Conta com várias publicações sobre as relações humanos/outros animais e colabora regularmente com o Programa de Pós-Graduação em Estudos da Cultura Contemporânea da Universidade Federal de Mato Grosso (Brasil). Exerce atividades de docência com regularidade em diversas instituições de ensino superior públicas e privadas.', 
            description_en='Doutorada em Psicologia pela Universidade de Stirling (Escola de Ciências Naturais), Escócia, Reino Unido. É atualmente investigadora do CIAS - Centro de Investigação em Antropologia e Saúde (Departamento de Ciências da Vida, Universidade de Coimbra). Os seus interesses de pesquisa são as percepções humanas sobre outras espécies animais e a biodiversidade em geral e como elas podem interferir nos esforços de conservação ambiental. Tem experiência de campo em África - em particular na Guiné-Bissau - e conhecimentos em análise quantitativa e qualitativa de dados. Conta com várias publicações sobre as relações humanos/outros animais e colabora regularmente com o Programa de Pós-Graduação em Estudos da Cultura Contemporânea da Universidade Federal de Mato Grosso (Brasil). Exerce atividades de docência com regularidade em diversas instituições de ensino superior públicas e privadas.',
            direction=True,
            position_pt='',
            position_en='',
            photo=photo.id,
            orcid='0000-0002-2766-0135'
        )
        db_session.add(profile)


        # Tania Minhos
        photo = file_models.UploadedFile(
            original_name = 'TaniaMinhos.jpg',
            file_path=os.path.join(app.root_path, '..', 'content', 'TaniaMinhos.jpg')
        )
        db_session.add(photo)

        profile = models.Profile(
            name='Tânia Minhós', 
            description_pt='Tânia Minhós is a Professor at the School of Social Sciences and Humanities of Universidade Nova de Lisboa (NOVA FCSH) since 2015 at the Anthropology department. She has conducted research in West Africa since 2008, focusing on sympatric primate species with different socio-ecologies to address questions related to their adaptive strategies to the human-led changes in their environments, namely the impacts and drivers of deforestation and hunting.  Recognizing the multi-layer dimensions of these challenges, Tânia’s research combines cross-disciplinary data (e.g. genetics, ecology, behavior, social), to address questions related to evolution and adaptation of non-human primates inhabiting anthropogenic habitats and to gain insights on the human-nonhuman primate interactions in fast-changing environments. The ultimate goal of her research is to bring local communities, conservation practitioners, and researchers together to develop strategies aiming at the sustainable coexistence of human communities and nonhuman primates in shared landscapes.', 
            description_en='Tânia Minhós is a Professor at the School of Social Sciences and Humanities of Universidade Nova de Lisboa (NOVA FCSH) since 2015 at the Anthropology department. She has conducted research in West Africa since 2008, focusing on sympatric primate species with different socio-ecologies to address questions related to their adaptive strategies to the human-led changes in their environments, namely the impacts and drivers of deforestation and hunting.  Recognizing the multi-layer dimensions of these challenges, Tânia’s research combines cross-disciplinary data (e.g. genetics, ecology, behavior, social), to address questions related to evolution and adaptation of non-human primates inhabiting anthropogenic habitats and to gain insights on the human-nonhuman primate interactions in fast-changing environments. The ultimate goal of her research is to bring local communities, conservation practitioners, and researchers together to develop strategies aiming at the sustainable coexistence of human communities and nonhuman primates in shared landscapes.',
            direction=True,
            position_pt='Presidente',
            position_en='President',
            photo=photo.id,
            orcid='0000-0003-0183-1343'
        )
        db_session.add(profile)


        # Filipa Borges
        photo = file_models.UploadedFile(
            original_name = 'FilipaBorges.jpg',
            file_path=os.path.join(app.root_path, '..', 'content', 'FilipaBorges.jpg')
        )
        db_session.add(photo)

        profile = models.Profile(
            name='Filipa Borges', 
            description_pt='Filipa Borges é estudante de doutoramento em Antropologia afiliada ao Centro em Rede de Investigação em Antropologia (CRIA-NOVA FCSH/IN2PAST), à Universidade de Exeter e à Universidade do Porto. O seu trabalho combina técnicas de genómica e de ciência social para estudar a interface entre primatas não-humanos e humanos na África Ocidental, principalmente na Serra Leoa.', 
            description_en='Filipa Borges is a PhD candidate in Anthropology affiliated with the Centre for Research in Anthropology (CRIA-NOVA FCSH/IN2PAST), the University of Exeter, and the University of Porto. Her work integrates genomics and social sciences methods to study the human/nonhuman primate interface in West Africa, particularly Sierra Leone.',
            direction=True,
            position_pt='',
            position_en='',
            photo=photo.id,
            orcid='0000-0002-1405-2341'
        )
        db_session.add(profile)


        image_file = file_models.UploadedFile(
            original_name='pexels-egor-kamelev-802208_small.jpg',
            file_path=os.path.join(app.root_path, 'static', 'img', 'pexels-egor-kamelev-802208_small.jpg')
        )
        db_session.add(image_file)

        image = models.Image(
             image_file.id,
             subtitle_pt='APP is happy to announce the IX Iberian Primatological Conference.The conference will take place in Vila do Conde from **21 to 23 November** 2024. Registration will be available from mid-April.', 
             subtitle_en='APP is happy to announce the IX Iberian Primatological Conference.The conference will take place in Vila do Conde from **21 to 23 November** 2024. Registration will be available from mid-April.', 
             alt_pt=None, 
             alt_en=None
        )
        db_session.add(image)
        db_session.commit()

        news = models.News(
            title_pt = 'IX Congresso Ibérico de Primatologia', 
            title_en = 'IX Iberian Primatological Conference', 
            body_pt  = "APP is happy to announce the IX Iberian Primatological Conference. \
                        The conference will take place in Vila do Conde from 21 to 23 November 2024. \
                        Registration will be available from mid-April. \
                        Stay tuned!", 
            body_en  =  "APP is happy to announce the IX Iberian Primatological Conference. \
                        The conference will take place in Vila do Conde from 21 to 23 November 2024. \
                        Registration will be available from mid-April. \
                        Stay tuned!"
        )
        db_session.add(news)

        news = models.News(
        title_pt = 'IX Congresso Ibérico de Primatologia', 
        title_en = 'IX Iberian Primatological Conference', 
        body_pt  = "APP is happy to announce the IX Iberian Primatological Conference. \
                    The conference will take place in Vila do Conde from **21 to 23 November** 2024. \
                    Registration will be available from mid-April. \
                    Stay tuned!", 
        body_en  =  "APP is happy to announce the IX Iberian Primatological Conference. \
                        The conference will take place in Vila do Conde from **21 to 23 November** 2024. \
                        Registration will be available from mid-April. \
                        Stay tuned!",
        image    =  image.id
        )
        db_session.add(news)

        news = models.News(
        title_pt = 'IX Congresso Ibérico de Primatologia', 
        title_en = 'IX Iberian Primatological Conference', 
        body_pt  = "APP is happy to announce the IX Iberian Primatological Conference. \
                    The conference will take place in Vila do Conde from **21 to 23 November** 2024. \
                    Registration will be available from mid-April. \
                    Stay tuned!", 
        body_en  =  "APP is happy to announce the IX Iberian Primatological Conference. \
                    The conference will take place in Vila do Conde from **21 to 23 November** 2024. \
                    Registration will be available from mid-April. \
                    Stay tuned!"
        )

        db_session.add(news)

        member = models.Member(given_name='Zé', family_name='Chimp', number=1, species='Homo Sapiens')
        db_session.add(member)

        member = models.Member(given_name='Tânia', family_name='Minhós', number=2, species='Colobo Vermelho')
        db_session.add(member)

        member = models.Member(given_name='Filipa', family_name='Borges', number=3, species='Chimpanzé')
        db_session.add(member)

        db_session.commit()

        news = db_session.get(models.News, 3)
        news.title_pt = 'Notícia modificada'
        news.title_en = 'Modified news'

        db_session.commit()

    click.echo('Initialized the database.')
