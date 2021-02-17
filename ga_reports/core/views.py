# Create your views here.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import pdb

SCOPES = [settings.GOOGLE_SCOPES["PRESENTATIONS"]["manager"], settings.GOOGLE_SCOPES["PRESENTATIONS"]["readonly"]]


class GoogleAuthorizationView(TemplateResponseMixin, ContextMixin, View):

    flow_class = Flow
    flow_redirect_uri = reverse_lazy('core:get_google_token')
    template_name = "core/google_authorization.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     print(self.request.GET.get('code'))
    #     context['status'] = self.request.GET.get('status')
    #     return context

    def get(self, request, *args, **kwargs):
        flow = self.flow_class.from_client_config(
            client_config=settings.GOOGLE_CLIENT_CONFIG, scopes=SCOPES)
        flow.redirect_uri = request.build_absolute_uri(str(self.flow_redirect_uri))
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

        request.session["state"] = state

        return HttpResponseRedirect(authorization_url)


google_auth = GoogleAuthorizationView.as_view()


class GoogleOAuth2CallbackView(TemplateResponseMixin, ContextMixin, View):

    flow_class = Flow
    flow_redirect_uri = reverse_lazy('core:get_google_token')
    template_name = "core/get_token.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     print(self.request.GET.get('code'))
    #     context['status'] = self.request.GET.get('status')
    #     return context

    def get(self, request, *args, **kwargs):
        state = request.session['state']

        flow = self.flow_class.from_client_config(
            client_config=settings.GOOGLE_CLIENT_CONFIG,
            scopes=SCOPES,
            state=state)
        flow.redirect_uri = request.build_absolute_uri(str(self.flow_redirect_uri))

        code = request.GET.get('code')

        flow.fetch_token(code=code)
        credentials = flow.credentials
        request.session['credentials'] = self.credentials_to_dict(credentials)

        return HttpResponseRedirect(reverse_lazy("core:test_google_api"))

    def credentials_to_dict(self, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}


get_google_token = GoogleOAuth2CallbackView.as_view()


class TestAPIGoogleView(TemplateResponseMixin, ContextMixin, View):

    template_name = "core/test_api.html"

    def get(self, request, *args, **kwargs):
        creds = Credentials(**request.session['credentials'])

        service = build('slides', 'v1', credentials=creds)

        # Call the Slides API
        PRESENTATION_ID = "1RQewldtZvvnzbg80gJWH9wbnLRnI0JWGPoJDYcRX1o8"
        # pdb.set_trace()

        # presentation = service.presentations().get(
        #     presentationId=PRESENTATION_ID).execute()

        body = {
            'requests': self.change_text()[1]
        }

        response = service.presentations() \
            .batchUpdate(presentationId=PRESENTATION_ID, body=body).execute()

        # slides = presentation.get('slides')

        # print('The presentation contains {} slides:'.format(len(slides)))
        # for i, slide in enumerate(slides):
        #     print(f"- Slide #{i + 1} contains {len(slide.get('pageElements'))} elements.")
        #     for key, value in slide.get('pageElements'):
        #         print(value.get())

        return self.render_to_response(self.get_context_data())

    def change_text(self):
        element_id = 'i0'

        requests_1 = [

            # Insert text into the box, using the supplied element ID.
            {
                'deleteText': {
                    'objectId': element_id,
                    # 'textRange': {
                    #     "startIndex": 0,
                    #     "endIndex": 3
                    #     "type": enum (Type)
                    # }
                    # 'textRange': 0
                }
            }
        ]
        requests_2 = [
            # Insert text into the box, using the supplied element ID.
            {
                'insertText': {
                    'objectId': element_id,
                    'insertionIndex': 0,
                    'text': 'New Box Text Inserted!'
                }
            }
        ]

        return [requests_1, requests_2]


test_google_api = TestAPIGoogleView.as_view()
