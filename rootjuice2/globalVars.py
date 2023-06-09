import collections


def init():
    #===== general =====
    global scraped_count
    global maxPagesPerSiteLimit
    global fonte
    global binFolder
    global tikaAppJar
    #===== Solr =====
    global solrIpAddress
    global solrPortNumber
    global solrCoreName
    global logLevel
    # ===== Postgres =====
    global pg_host
    global pg_port
    global pg_database
    global pg_user
    global pg_password

    scraped_count = collections.defaultdict(int)
    maxPagesPerSiteLimit = 9000 # supposed to be unlimited
    binFolder = ""
    tikaAppJar = ""
    fonte = "website"
    solrIpAddress = "localhost"
    solrPortNumber = "8983"
    solrCoreName = "documenti"
    logLevel = "logging.INFO"

    pg_database = "foia"
    pg_user = "postgres"
    pg_password = "password"
    #pg_host = "postgres"  # docker
    #pg_port = "5432"  # docker
    pg_host = "localhost"  # locale
    pg_port = "5433"  # locale