from django.http.response import JsonResponse
from django.utils.dateparse import parse_date
from django_filters import filterset
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets, generics
from rest_framework import views
from rest_framework import response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView, get_object_or_404
import json
from django.http import HttpResponse

from core.filters import NumberofFilter, RaCampusFilter, StudentsFilter

from .models import Students
from .serializers import CampusSerializer, StudentsSerializer


class StudentsListView(generics.ListAPIView):

    """

    (Desafio item 1)
    View to list all students in the collection

    * Filter by 'data_inicio'; format: yy-mm-dd 
    query parameter
    * Filter by 'data_fim'; format: yy-mm-dd 
    query parameter
    * Filter by 'modalidade' query parameter


    """

    serializer_class = StudentsSerializer
    queryset = Students.objects.all().order_by('-data_inicio')
    filter_backends = [DjangoFilterBackend]
    filter_class = StudentsFilter
    filterset_fields = ['modalidade', 'data_inicio']


class CampusListView(generics.ListAPIView):

    """
    (Desafio item 2)

    View to list a Campus and its corresponding
    courses. It's filtred by the document, so
    there is no aggregation of courses by campus.

    * Filter by 'campus' query parameter

    """
    serializer_class = CampusSerializer
    queryset = Students.objects.values('campus', 'curso')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['campus']


class NumberOfStudentsListView(generics.ListAPIView):

    """
    (Desafio item 3)

    View to list all students in the collection

    * Filter by 'data_inicio'; format: yy-mm-dd 
    query parameter
    * Filter by 'data_fim'; format: yy-mm-dd 
    query parameter
    * Filter by 'campus' query parameter

    Returns the count, or sum, of documents relative to the
    parameters.
    """

    serializer_class = StudentsSerializer
    queryset = Students.objects.all()
    # filter_backends = [DjangoFilterBackend]
    # filter_class = NumberofFilter
    # filterset_fields = ['campus', 'data_inicio']

    def get(self, request):
        resp = Students.objects.all()

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        campus = self.request.query_params.get('campus')

        if start_date and end_date and campus:
            resp = resp.filter(data_inicio__gte=start_date,
                                       data_inicio__lte=end_date
                                       ).filter(campus=campus).count()

        else:

            resp = {
                'error': {
                    'start_date parameter': 'yy-mm-dd',
                    'end_date parameter': 'yy-mm-dd',
                    'campus': [
                        'AQ',
                        'CB',
                        'CG',
                        'CX',
                        'DR',
                        'JD',
                        'NV',
                        'PP',
                        'TL',
                    ]

                }
            }

        return Response({'Number of students': resp})


class CreateStudent(generics.ListCreateAPIView):
    """
    (Desafio item 4)

    View to create a student document. 
    """

    serializer_class = StudentsSerializer
    queryset = Students.objects.all()
    filter_backends = [DjangoFilterBackend]


class SearchStudent(generics.ListAPIView):

    """
    (Desafio item 5)

    View to search a student document.

    * Filter by 'ra', this view doesn't
    allow search by substring.

    Nota: Tentei fazer esta view passando
    o 'ra' como 'url value', porém 'ra' não
    é um campo com uma unique key. No dataset
    há repetição de aluno por haver mais de
    um curso cadastro em seu nome.
    """

    serializer_class = StudentsSerializer
    queryset = Students.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ra']


class StudentsDetail(APIView):

    """
    View to get a certain document. 

    URL values needed:

    * Ra
    * Campus

    /students/{ra}/{campus}

    """

    def get_object(self, request, *args, **kwargs):
        ra = self.kwargs.get('ra')
        campus = self.kwargs.get('campus')
        try:
            resp = get_object_or_404(Students, ra=ra, campus=campus)
        except Students.MultipleObjectsReturned:
            resp = Students.objects.all()

        return resp

    def get(self, request, ra, campus):
        student = self.get_object(ra, campus)

        try:
            serializer = StudentsSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AttributeError:
            response_error = {
                'Error': 'Mutiple objects returned',
            }

            return JsonResponse(response_error)

    def delete(self, request, ra, campus):
        student = self.get_object(ra, campus)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
