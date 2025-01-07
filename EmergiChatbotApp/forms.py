from django import forms


class QuestionForm(forms.Form):
    ROLE_CHOICES = [('Mentees', 'Mentees'), ('Mentors', 'Mentors')]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Select Role",
        widget=forms.Select(attrs={
            'class': 'block bg-transparent border border-slate-700 placeholder-slate-200 text-slate-200 w-full p-2 py-3 rounded-md mb-2  transition-all duration-300 text-sm'
        })
    )
    question = forms.CharField(
        max_length=1000,
        label="Ask a Question",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'block bg-transparent border border-slate-700 placeholder-slate-200 text-slate-200 w-full p-2 py-3 rounded-md mb-4  transition-all duration-300 text-sm',
            'rows': 4,  # Adjust the number of rows according to your needs
            'placeholder': 'Type your question here...',
        })
    )
