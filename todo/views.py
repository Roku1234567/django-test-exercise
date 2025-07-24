
from django.shortcuts import render, redirect

from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task

# Create your views here.


def index(request):
    # POST のときだけタスクを作成
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            # due_at を安全にパース
            due_at = None
            due_at_str = request.POST.get('due_at', '').strip()
            if due_at_str:
                dt = parse_datetime(due_at_str)
                if dt is not None:
                    due_at = make_aware(dt)

            # content も取得
            content = request.POST.get('content', '').strip()

            # 新規作成
            Task.objects.create(
                title=title,
                due_at=due_at,
                content=content,
            )
        # → redirect はせずにこのまま下の一覧取得＋renderへ

    # GET／POST 後ともに一覧を取得してレンダー
    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    return render(request, 'todo/index.html', {'tasks': tasks})
def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    return render(request, 'todo/detail.html', {'task': task})



def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method == 'POST':
        # タイトル更新
        new_title = request.POST.get('title', '').strip()
        if new_title:
            task.title = new_title

        # due_at 更新／クリア
        due_at_str = request.POST.get('due_at', '').strip()
        if due_at_str:
            dt = parse_datetime(due_at_str)
            if dt:
                task.due_at = make_aware(dt)
        else:
            task.due_at = None

        # 内容更新
        task.content = request.POST.get('content', '').strip()

        task.save()
        return redirect('detail', task_id=task.id)

    return render(request, 'todo/edit.html', {'task': task})

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect('index')
def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect('index')


