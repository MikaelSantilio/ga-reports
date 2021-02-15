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
            client_config=settings.GOOGLE_CLIENT_SETTINGS, scopes=settings.GOOGLE_SCOPES["PRESENTATIONS"]["readonly"])
        flow.redirect_uri = request.build_absolute_uri(self.flow_redirect_uri)
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

        request["state"] = state

        return HttpResponseRedirect(authorization_url)

# get_google_token = GetGoogleTokenView.as_view()


class GoogleOAuth2CallbackView(TemplateResponseMixin, ContextMixin, View):

    template_name = "core/get_token.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     print(self.request.GET.get('code'))
    #     context['status'] = self.request.GET.get('status')
    #     return context

    def get(self, request, *args, **kwargs):
        state = request.session['state']

        flow = self.flow_class.from_client_config(
            client_config=settings.GOOGLE_CLIENT_SETTINGS,
            scopes=settings.GOOGLE_SCOPES["PRESENTATIONS"]["readonly"],
            state=state)
        flow.redirect_uri = request.build_absolute_uri(self.flow_redirect_uri)

        code = request.GET.get('code')

        flow.fetch_token(code=code)
        credentials = flow.credentials
        request.session['credentials'] = self.credentials_to_dict(credentials)

        return HttpResponseRedirect(authorization_url)

    def credentials_to_dict(self, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}


get_google_token = GetGoogleTokenView.as_view()


class TestAPIGoogleView(TemplateResponseMixin, ContextMixin, View):

    template_name = "core/get_token.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     print(self.request.GET.get('code'))
    #     context['status'] = self.request.GET.get('status')
    #     return context

    def get(self, request, *args, **kwargs):
        creds = google.oauth2.credentials.Credentials(**request.session['credentials'])

        service = build('slides', 'v1', credentials=creds)

        # Call the Slides API
        presentation = service.presentations().get(
            presentationId=PRESENTATION_ID).execute()
        slides = presentation.get('slides')

        print('The presentation contains {} slides:'.format(len(slides)))
        for i, slide in enumerate(slides):
            print(f"- Slide #{i + 1} contains {len(slide.get('pageElements'))} elements.")

        return self.render_to_response(self.get_context_data())

    def credentials_to_dict(self, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}


get_google_token = GetGoogleTokenView.as_view()
