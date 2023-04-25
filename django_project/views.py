import jsonpickle
from django.shortcuts import redirect, render
from django.views import View
from django.template.loader import get_template
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
from django.template import loader

class GoogleCalendarInitView(View):
  def get(self, request):
    
    # Load client secrets from a JSON file
    with open("client_secret.json", "r") as f:
      
      client_secrets = json.load(f)  
      
      flow = InstalledAppFlow.from_client_config(client_secrets, scopes=["https://www.googleapis.com/auth/calendar.events"])
      flow.redirect_uri = 'https://convinassignment.shreyas997.repl.co'

      authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
      print("------>",authorization_url)

      request.session["oauth_state"] = state
      request.session["oauth_flow"] = jsonpickle.encode(flow)
        
      return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        error = loader.get_template('Templates/errors.html')
        events = loader.get_template('Templates/events.html')
        home = loader.get_template('Templates/home.html')
        print("=-=-=-=>",error)
        
        code = request.GET.get('code')
        state = request.GET.get('state')

        print("code====>", code)
        if state != request.session.get('oauth_state'):
            return render(request, error_template, {'error': 'Invalid state'})
        flow_json = request.session.pop("oauth_flow", None)
        if flow_json is None:
            return render(request, error_template, {'error': 'No OAuth flow found in session.'})
        flow = jsonpickle.decode(flow_json)
        credentials = flow.fetch_token(code=code)
            
        service = build('calendar', 'v3', credentials=credentials)
            
        events_result = service.events().list(calendarId='primary', maxResults=10,singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        return render(request, events_template, {'events': events})


def home(request):
    # Load the template
    template = get_template('home.html')
    
    # Render the template with the request
    return render(request, template)
