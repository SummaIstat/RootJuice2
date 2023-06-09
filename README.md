# RootJuice2 readme     

## What is RootJuice2 and what is it intended to be used for

RootJuice2 is the successor of RootJuice.

In a nutshell, RootJuice2 is a Python application that takes as input a list of URLs and on the basis of some configurable parameters retrieves the textual content of that URLs and saves it in an Apache Solr collection.

More in details it takes as input 2 files :
<ul>
<li> seed.tsv ==> list of URLs to be scraped</li>
<li> config.cfg ==> list of technical parameters that you can modify on your needs</li>
</ul>	

I developed and used this program for 2 different use cases:
1) scrape only the homepages of the URLs listed in the input file seed.tsv
2) scrape several pages of the URLs listed in the input file seed.tsv

On the basis of the use case it is necessary to change the configuration parameters contained in the input file config.cfg accordingly.


## How is the project folder made

The RootJuice2 folder is a PyCharm project ready to be run or modified in the IDE (you just have to import the project and optionally change some configuration parameters in the code).

Under the main directory you can find:
1) .idea => the folder containing the PyCharm ide configuration
2) conf => the folder containing the config.cfg file to be customized
3) logs => the folder containing the log files of the program execution
4) rootjuice2 => the folder containing the source code
5) solr-8.11.1 => the folder containing a preconfigured Solr configuration
6) LICENSE => copy of the EUPL v1.2 license
7) README.md => this file
8) scrapy.cfg => a configuration file (you are not supposed to modify this file)
9) seed.tsv => list of URLs to be scraped

As you probably already know it is definitely not a good practice to put all this stuff into a downloadable project folder, but i decided to break the rules in order to facilitate your job. Having all the stuff that will be necessary in just one location and by following the instructions you should be able to test the whole environment in 5-10 minutes.

## How to execute the program on your PC by using the terminal

If you have Python 3.X and Java already installed on your PC you just have to apply the following instruction points:

1) create a folder on your filesystem (let's say "rootjuice2")

2) copy the content of the project directory into "rootjuice2"

3) customize the parameters inside the config.cfg file :
        
        Change the value of the path related parameters (eg. BIN_FOLDER,TIKA_APP_JAR,LOG_FILE_FOLDER) according with the position of the files and folders on your filesystem.

4) open a terminal and go into the rootjuice2 directory

5) I suggest to create and configure a virtual environment by entering the following commands (by the way I use conda to do this):
        <ul>
	<li> conda create --name rootjuice2 python=3.9</li>
        <li> conda activate rootjuice2</li>
        <li> pip install -r requirements.txt</li>
	</ul>

6) in the same terminal go into the solr-8.11.1/bin sub-directory and enter the following command to start Solr:
        <ul>
	<li> solr start</li>
	</ul>

7) wait a few seconds, then open the following URL in your browser in order to check that Solr is up and running:
        </br> http://localhost:8983/solr/#/

8) in another tab of your browser visit the following link to delete all the documents in the Solr collection named "test":
        </br> http://127.0.0.1:8983/solr/test/update?commit=true&stream.body=%3Cdelete%3E%3Cquery%3E*:*%3C/query%3E%3C/delete%3E

9) in the same terminal go into the rootjuice2 main directory and enter the following command to start the rootjuice2 program that will scrape the URLs contained in the seed.tsv file:
        </br>
	</br>
	scrapy crawl rjSpider -a seedFilePath=C:/rootjuice2/seed.tsv -a confFilePath=C:/rootjuice2/conf/config.cfg -s JOBDIR=C:/rootjuice2/conf/JOBDIR/rj2Spider_jobdir/

10) at the end of execution you should find:
	<ul>
	<li>a log file called rootjuice2_[dateTime].log inside the "logs" directory</li>
	<li>the scraped webpages stored in the Solr collection named "test"</li>
	</ul>

11) in order to verify that the textual content of the webpages has been correctly stored into Solr:
	<ul>
        <li> open the url http://localhost:8983/solr/#/</li>
        <li> in the left bar chose the test collection from the combo box</li>
        <li> in the left bar click the "Query" link</li>
        <li> in the main panel click the "Execute Query" button</li>
        <li> you shoul see the content of the downloaded webpages</li>
	</ul>

12) to stop Solr, in the same terminal you used so far, go into the solr-8.11.1/bin sub-directory and enter the following command:
	<ul>
        <li> solr stop -all</li>
        <ul>

## Licensing

This software is released under the European Union Public License v. 1.2
</br>A copy of the license is included in the project folder.


## Considerations

This program is still a work in progress so be patient if it is not completely fault tolerant; in any case feel free to contact me (donato.summa@istat.it) if you have any questions or comments.
