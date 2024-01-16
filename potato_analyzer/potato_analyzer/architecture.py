from diagrams import Cluster, Diagram, Edge

from diagrams.azure.database import DataLake, DatabaseForPostgresqlServers
from diagrams.onprem.database import Postgresql
from diagrams.programming.language import Python, Javascript
from diagrams.k8s.controlplane import API
from diagrams.aws.analytics import DataPipeline


with Diagram("The Potato App", show=False):
    datalake = DataLake("delta lake")

    with Cluster("Potato Analyzer"):
        openai = API("OpenAI")
        datalake >> Edge() << Python("pipelines") >> openai
        openai - [API("GPT-4"), API("DALL-E 3")]

    with Cluster("Potato WebApp"):
        with Cluster("Backend"):
            postgres = Postgresql("postgres")
            flask = Python("Flask")
            graphql = Python("GraphQL")
            datalake >> DataPipeline("Delta Sharing") >> postgres >> Edge() << flask >> graphql

        with Cluster("Frontend"):
            graphql >> Javascript("Vue.js") >> Javascript("Vueify")
