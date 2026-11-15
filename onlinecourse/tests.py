from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Choice, Course, Enrollment, Question, Submission


class ExamModelTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(name='Python')
        self.question = Question.objects.create(
            course=self.course, question_text='Select correct answers', grade=5
        )
        self.correct = Choice.objects.create(
            question=self.question, choice_text='Correct', is_correct=True
        )
        self.second = Choice.objects.create(
            question=self.question, choice_text='Also correct', is_correct=True
        )
        self.wrong = Choice.objects.create(
            question=self.question, choice_text='Incorrect'
        )

    def test_score_requires_all_correct_choices_and_no_incorrect_choices(self):
        self.assertTrue(self.question.is_get_score(
            [str(self.correct.pk), str(self.second.pk)]
        ))
        for selected in ([], [self.correct.pk], [self.wrong.pk],
                         [self.correct.pk, self.second.pk, self.wrong.pk]):
            with self.subTest(selected=selected):
                self.assertFalse(self.question.is_get_score(selected))

    def test_question_without_correct_choices_does_not_award_points(self):
        question = Question.objects.create(course=self.course, question_text='Empty')
        self.assertFalse(question.is_get_score([]))

    def test_enrollment_supports_multiple_submissions_with_shared_choices(self):
        user = get_user_model().objects.create_user(username='learner')
        enrollment = Enrollment.objects.create(user=user, course=self.course)
        first = Submission.objects.create(enrollment=enrollment)
        second = Submission.objects.create(enrollment=enrollment)
        first.choices.add(self.correct, self.second)
        second.choices.add(self.correct)
        self.assertEqual(enrollment.submission_set.count(), 2)
        self.assertEqual(first.choices.count(), 2)
        self.assertEqual(self.correct.submission_set.count(), 2)

    def test_course_deletion_cascades_to_exam_models(self):
        self.course.delete()
        self.assertFalse(Question.objects.exists())
        self.assertFalse(Choice.objects.exists())
