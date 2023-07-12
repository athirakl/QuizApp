from django.shortcuts import render,redirect

from django.contrib.auth.models import User

from quiz.models import Category,Questions,Answers,QuizRecord
from quiz.forms import RegistrationForm,LoginForm

from django.contrib.auth import login,logout,authenticate

from django.urls import reverse_lazy

from django.views.generic import CreateView,ListView,UpdateView,DetailView,TemplateView,View,FormView

# Create your views here.


class RegistrationView(CreateView):
    
    model=User
    form_class=RegistrationForm
    template_name="register.html"
    success_url=reverse_lazy("signin")
    

class SignInView(FormView):
    form_class=LoginForm
    template_name="login.html"
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                return redirect("home")
        return render(request,self.template_name,{"form":form})
        
            

class HomeView(TemplateView):
    template_name="home.html"



def signout(request,*args,**kwargs):
    logout(request)
    return redirect("signin")


class QuizHomeView(View):
    def get(self,request,*args,**kwargs):
        qs=Category.objects.all()
        return render(request,"quiz-home.html",{"cats":qs})
    
    def post(self,request,*args,**kwargs):
        
        cat=request.POST.get("category")
        mode=request.POST.get("mode")
        return redirect("question-list",cat=cat,mode=mode)
    



from django.db.models import Sum
    

class QuestionListView(View):

    def get(self,request,*args,**kwargs):
        category=kwargs.get("cat")
        mode=kwargs.get("mode")
        qs=list(Questions.objects.filter(category__topic=category,mode=mode))
        return render(request,"question-list.html",{"questions":qs})
    
    def post(self,request,*args,**kwargs):
        data=request.POST.dict()
        print(data)
        data.pop('csrfmiddlewaretoken')
        questions_attended=len(data)
       
        mark_obtained=0
        wrong_answer=0
        for q,ans in data.items():
            question=Questions.objects.get(question=q)
            right_answer=question.answer
            if(right_answer.options==ans):
                mark_obtained=mark_obtained+question.mark
            else:
                wrong_answer+=1

            right_answer_count=questions_attended-wrong_answer
        category=kwargs.get("cat")
        mode=kwargs.get("mode")
        result=''
        total=Questions.objects.filter(category__topic=category,mode=mode).aggregate(Sum('mark')).get('mark__sum')
        if total/2 <=mark_obtained:
            result="pass"
        else:
            result="failed"
        data=QuizRecord.objects.create(mark_obtained=mark_obtained,right_answer_count=right_answer_count,wrong_answer_count=wrong_answer,user=request.user)
        return render(request,"quiz-mark.html",{'mark_obtained':mark_obtained,'question_attended':questions_attended,"result":result})
    

