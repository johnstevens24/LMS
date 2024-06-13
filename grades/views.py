from django.shortcuts import render
from . import models
from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
from django.contrib.auth.models import Group
from django.db.models.functions import Coalesce
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

def is_student(user):
    return user.groups.filter(name="Students").exists()

def isSupervisor(user):
    return user.is_superuser

def isTA(user):
    return user.groups.filter(name="Teaching Assistants").exists()

def is_ta(user):
    if user.groups.filter(name="Teaching Assistants").exists():
        return True
    if user.is_superuser:
        return True
    return False

def pick_grader(Assignment):  
    # TAs = Group.objects.get(name = 'Teaching Assistants').user_set.all().filter(graded_set__assignment = Assignment)
    return Group.objects.get(name='Teaching Assistants').user_set.annotate(total_assigned=Coalesce(Count("graded_set__assignment", filter=Q(graded_set__assignment=Assignment)), 0)).order_by('total_assigned').first()

# Create your views here.

@login_required
def assignments(request):
    assgnmnts = models.Assignment.objects.all()
    return render(request, "assignments.html", {"title": "CS3550 Assignments", "assignments": assgnmnts})

@login_required
def index(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id=assignment_id)

        if is_student(request.user):
            notYetDue = (assignment.deadline.date() >= datetime.now().date())
            studentMessage = 'default'

            #if a submission for this user exists
            if models.Submission.objects.filter(assignment = assignment, author = request.user):
                submission = models.Submission.objects.filter(author= request.user, assignment__id = assignment.id).first()
                messagePartTwo= ''

                #if its been graded
                if models.Submission.objects.filter(assignment = assignment, author = request.user, score__isnull = False):
                    studentMessage = "Your submission, "
                    messagePartTwo = ", received " + str(submission.score) + "/" + str(assignment.points) + " points (" + str(round((submission.score/assignment.points)*100, 2)) + "%)"
                else:
                    #if its not due yet
                    if notYetDue:
                        studentMessage = "Your current submission is "
                    else:
                        studentMessage = "Your submission, "
                        messagePartTwo = ", is being graded"
                return render(request, "index.html", 
                          {"title": assignment.title, 
                           "assignment": assignment, 
                           "isTA": isTA(request.user), 
                           "isSupervisor": isSupervisor(request.user), 
                           "isStudent": is_student(request.user), 
                           "studentMessage": studentMessage, 
                           "notYetDue":notYetDue, 
                           "assignment_id":assignment_id,
                           "hasSubmission":True,
                           "sub":submission,
                           "messagePartTwo": messagePartTwo
                           })

            else:
                #if its not due yet
                if notYetDue:
                    studentMessage = "No current submission"
                else:
                    studentMessage = "You did not submit this assignment and recieved 0 points"
                return render(request, "index.html", 
                          {"title": assignment.title, 
                           "assignment": assignment, 
                           "isTA": isTA(request.user), 
                           "isSupervisor": isSupervisor(request.user), 
                           "isStudent": is_student(request.user), 
                           "studentMessage": studentMessage, 
                           "notYetDue":notYetDue, 
                           "assignment_id":assignment_id,
                           "hasSubmission":False
                           })

        else:
            subCount = 0
            myCount = 0
            listOfSubmissions = models.Submission.objects.all()
            for s in listOfSubmissions:
                if (s.assignment.id == assignment_id):
                    subCount+=1
                    if(s.grader == request.user):
                        myCount+=1
            studentCount = models.Group.objects.get(name="Students").user_set.count()
            #studentCount = 0
            
            return render(request, "index.html", {"title": assignment.title, "assignment": assignment, "subCount":subCount, "myCount": myCount, "studentCount": studentCount, "isTA": isTA(request.user), "isSupervisor": isSupervisor(request.user)})
    except:
        raise Http404("Assignment Not Found")

@user_passes_test(is_student)
def submit(request, assignment_id):
    #check if its past due
    assignment = models.Assignment.objects.get(id=assignment_id)

    if assignment.deadline.date() < datetime.now().date():
        #raise http400 error
        return HttpResponse("This assignment is past its due date", status=400)
    
    #if there exists a submission
    if models.Submission.objects.filter(assignment = assignment, author = request.user):
        submission = models.Submission.objects.filter(author= request.user, assignment__id = assignment.id).first()
        submission.file = request.FILES["submissionFile"]
        submission.save()
    #if there doesn't exist a submission
    else:
        submission = models.Submission()
        submission.file = request.FILES["submissionFile"]
        submission.author = request.user
        submission.assignment = assignment
        submission.grader = pick_grader(assignment)
        submission.save()

    #redirect back to the assignment's page
    return redirect("/"+str(assignment_id)+"/")

@login_required
@user_passes_test(is_ta)
def submissions(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id = assignment_id)
        submissions = []
        if isSupervisor(request.user):
            submissions = models.Submission.objects.filter(assignment__id = assignment_id)
        if isTA(request.user):
            submissions = models.Submission.objects.filter(assignment__id = assignment_id, grader__id = request.user.id)

        submissions = submissions.order_by('author__username')

        return render(request, "submissions.html", {"title": assignment.title +" submissions", "assignment": assignment, "submissions": submissions, "assignment_id": assignment_id})
    except:
        raise Http404("Assignment Doesn't Exist")

@login_required
def show_upload(request, filename):
    if(models.Submission.objects.filter(file = filename)):
        submission = models.Submission.objects.filter(file = filename).first()
        if(submission.author == request.user or submission.grader == request.user or isSupervisor(request.user)):
            # print(str(submission.file))
            with submission.file.open() as fd:
                response = HttpResponse(fd)
                response["Content-Disposition"] = \
                f'attachment; filename="{submission.file.name}"'
                return response
            
        else:
            raise PermissionDenied
    else:
        #submission not found
        raise Http404("submission not found")

@login_required
def profile(request):
    assgnmnts = models.Assignment.objects.all()
    assignmentSubs = []
    gradedAssignments = []

    #for student view
    assignmentGrade = []
    earnedPoints = 0
    totalWeight = 0
    finalGrade = -1
    assignmentWeight = []
    for a in assgnmnts:
        if(isSupervisor(request.user)):
            subCount = models.Submission.objects.filter(assignment__id = a.id).count()
            gradedCount = models.Submission.objects.filter(assignment__id = a.id, score__isnull = False).count()
        else:
            subCount = models.Submission.objects.filter(grader__id = request.user.id, assignment__id = a.id).count()
            gradedCount = models.Submission.objects.filter(grader__id = request.user.id, assignment__id = a.id, score__isnull = False).count()
        assignmentSubs.insert(0, subCount)
        gradedAssignments.insert(0, gradedCount)

        if(is_student(request.user)):
            assignmentWeight.insert(0,a.weight)
            #if there exists a submission for this assignment by this user
            if models.Submission.objects.filter(author= request.user, assignment__id = a.id):
                #if its been graded
                if models.Submission.objects.filter(author= request.user, assignment__id = a.id, score__isnull = False):
                    score = models.Submission.objects.filter(author= request.user, assignment__id = a.id).first().score 
                    displayScore = (score / a.points ) * 100
                    assignmentGrade.insert(0, str(round(displayScore, 2)) + "%")
                    totalWeight += a.weight
                    earnedPoints += (score/a.points)*a.weight
                    
                else: #if it hasn't been graded
                    assignmentGrade.insert(0, "Ungraded")

            #if there doesn't exist a submission for this assingment
            else:
                if(a.deadline.date() >= datetime.now().date()):
                    assignmentGrade.insert(0, "Not Due")
                else:
                    assignmentGrade.insert(0, "Missing")
                    totalWeight += a.weight
            
    if earnedPoints == 0:
        finalGrade = 0
    else:
        if totalWeight == 0:
            finalGrade = 100
        else:
            finalGrade = round((earnedPoints/totalWeight)*100, 2)   
            
    
    return render(request, "profile.html", 
                  {"title": "CS3550 - Profile",
                   "assignments": assgnmnts, 
                   "submissionCounts": assignmentSubs, 
                   "gradedCount": gradedAssignments, 
                   "user": request.user, 
                   "isTA": isTA(request.user), 
                   "isSupervisor": isSupervisor(request.user),
                   "isStudent": is_student(request.user),
                   "assignmentGrade": assignmentGrade,
                   "finalGrade": finalGrade,
                   "assignmentWeight": assignmentWeight
                   })


def login_form(request):
    if(request.method == "GET"):
        nextPage = '/profile/'
        if 'next' in request.GET:
            nextPage = request.GET['next']

        return render(request, "login.html", {"nextPage": nextPage, "error": None})
    else:
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username = username, password = password)
        
        if(user is not None):
            login(request, user)
            print(username + " has logged in ") # you can ignore this
            return redirect(request.POST['next'])
        else:
            nextPage = '/profile/'
            if 'next' in request.POST:
                nextPage = request.POST['next']
            return render(request, "login.html", {"nextPage": nextPage, "error": "Username and password do not match"})

def logout_form(request):
    logout(request)
    return redirect("/profile/login")

@login_required
@user_passes_test(is_ta)
def grade(request, assignment_id):
    try:
        fields = request.POST
        for x in fields:
            if(x.startswith("grade-")):
                submissionID = x.split('-')
                submissionID = int(submissionID[1])
                submission = models.Submission.objects.get(id = submissionID)
                TAvalue = request.POST['grade-'+str(submissionID)]
                try:
                    TAvalue = float(TAvalue)
                    submission.score = TAvalue
                except ValueError:
                    submission.score = None
                submission.save()
                
        return redirect("/"+str(assignment_id)+"/submissions")
    except:
        raise Http404("Invalid Assignment or Submission")