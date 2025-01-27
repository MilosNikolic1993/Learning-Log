from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
from django.http import Http404


def index(request):
    """The home page for Learning Log."""
    return render(request, 'learning_logs/index.html')

@login_required()
def topics(request):
    """Show all topics."""
    topics = Topic.objects.order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required()
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = get_object_or_404(Topic, id=topic_id)
    # Make sure the topic belongs to the current user
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Add a new topic."""
    # Create a form instance, populated with POST data or an empty form
    form = TopicForm(request.POST or None)

    # Check if the request is a POST request and if the form is valid
    if request.method == 'POST' and form.is_valid():
        # Create a new topic but don't save it yet
        new_topic = form.save(commit=False)
        # Set the owner of the topic to the currently logged-in user
        new_topic.owner = request.user
        # Save the new topic in the database
        new_topic.save()
        # Redirect the user to the list of topics
        return redirect('learning_logs:topics')

    # If the form is not valid or if it's a GET request, render the form again
    return render(request, 'learning_logs/new_topic.html', {'form': form})

    return render(request, 'learning_logs/new_topic.html', {'form': form})

@login_required()
def new_entry(request, topic_id):
    """ Add a new entry for a topic """
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # Initial request; create a blank form
        form = EntryForm()
    else:
        # POST data submitted; process the data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required()
def edit_entry(request, entry_id):
    """ Edit an existing entry """
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process the data
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
