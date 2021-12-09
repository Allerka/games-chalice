from chalice import Chalice, Response
import os
import jinja2
from chalicelib.api import API

app = Chalice(app_name='gamestats')
app.debug = True

# master method for rendering all templates
def render(tpl_path, context):
	path, filename = os.path.split(tpl_path)
	return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)

# homepage with navigation list
@app.route('/', methods=['GET'])
def index():
	context = {'navlist': [
		{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/status', 'caption': 'View server status'},
  		{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/rankings/challenger/RANKED_SOLO_5x5', 'caption': 'See ranking info for the Challenger League - Ranked Solo 5x5 queue'},
		{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/rankings/challenger/RANKED_FLEX_SR', 'caption': 'See ranking info for the Challenger League - Ranked Flex SR queue'},
	 	{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/rankings/master/RANKED_SOLO_5x5', 'caption': 'See ranking info for the Master League - Ranked Solo 5x5 queue'},
		{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/rankings/master/RANKED_FLEX_SR', 'caption': 'See ranking info for the Master League - Ranked Flex SR queue'},
	 	{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/rankings/grandmaster/RANKED_SOLO_5x5', 'caption': 'See ranking info for the Grandmaster League - Ranked Solo 5x5 queue'},
		{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/rankings/grandmaster/RANKED_FLEX_SR', 'caption': 'See ranking info for the Grandmaster League - Ranked Flex SR queue'},
	 	{'href': 'https://rhw1cnyqe8.execute-api.us-east-1.amazonaws.com/api/featured', 'caption': 'View info on featured game replays'},
	]}
	template = render("chalicelib/templates/home.html", context)
	return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

# server status
@app.route('/status', methods=['GET'])
def status():
	context = API.api_status()
	template = render("chalicelib/templates/status.html", context)
	return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

# ranking results
@app.route('/rankings/{category}/{queue}', methods=['GET'])
def rankings(category, queue):
	context = API.api_rankings(category, queue)
	template = render("chalicelib/templates/rankings.html", context)
	return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

# featured game info
@app.route('/featured', methods=['GET'])
def featured():
	context = API.api_featured()
	template = render("chalicelib/templates/featured.html", context)
	return Response(template, status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})
