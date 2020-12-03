from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ApprovalsSerializer
from . models import Approvals
from rest_framework import viewsets
from rest_framework import status
from . forms import MyForm
from django.contrib import messages

import numpy as np
import pandas as pd
import joblib
from keras.models import load_model
# Create your views here.


class ApprovalsViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows users to be viewed or edited.
	"""
	if len(Approvals.objects.all()) >2:
		queryset = Approvals.objects.all()[:2]
		serializer_class = ApprovalsSerializer
	else:
		queryset = Approvals.objects.all()
		serializer_class = ApprovalsSerializer


@api_view(['GET'])
def Home(request):
    api_urls={
		'Create and visualize a json input for the ML model': '/api',
		'make prediction': '/status',
			  }
    return Response(api_urls)


@api_view(['POST'])
def DumifyData(request):

	serializer= ApprovalsSerializer(data= request.data)
	if serializer.is_valid():
		myDict = (request.data)
		print(myDict)
		df = pd.DataFrame(myDict, index=[0])
		print(df)
		df = df.drop(['Firstname', 'Lastname'], axis=1)

		cat_columns = ['Gender', 'Married', 'Education', 'Self_Employed', 'Property_Area']
		df = pd.get_dummies(df, columns=cat_columns)
		ohe_col = joblib.load("dm_x.pkl")

		newdict = {}
		for i in ohe_col:
			if i in df.columns:
				newdict[i] = df[i].values[0]
			else:
				newdict[i] = 0
	return Response(newdict)


@api_view(['POST'])
def approvereject(request):

	try:
		mdl = load_model('Mlmodel.h5')
		mydata = request.data
		unit = np.array(list(mydata.values()))
		unit = unit.reshape(1, -1)
		scalers = joblib.load("scaler.pkl")
		X=scalers.transform(unit)
		y_pred=mdl.predict(X)
		y_pred=(y_pred>0.58)
		newdf=pd.DataFrame(y_pred, columns=['Status'])
		newdf=newdf.replace({True:'Approved', False:'Rejected'})
		return Response({'status': newdf['Status'][0]})
		#return ('you status is {}'.format(newdf['Status'][0]))
	except ValueError as e:
		return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


def FormClient(request):

	form = MyForm()

	if request.method == 'POST':
		form = MyForm(request.POST)
		if form.is_valid():
			myDict = (request.POST).dict()
			df=pd.DataFrame(myDict, index=[0])
			df= df.drop(['csrfmiddlewaretoken', 'Firstname', 'Lastname'], axis=1)


			cat_columns = ['Gender', 'Married', 'Education', 'Self_Employed', 'Property_Area']
			df= pd.get_dummies(df, columns=cat_columns)
			ohe_col = joblib.load("dm_x.pkl")

			newdict={}
			for i in ohe_col:
				if i in df.columns:
					newdict[i]= df[i].values
				else:
					newdict[i]= 0

			newdf= pd.DataFrame(newdict)
			answer=approvereject(newdf)
			print(answer)
			messages.success(request, 'Application Status: {}'.format(answer))


	context = {'form': form}

	return render(request, 'MyAPI/FormClient.html', context=context)
