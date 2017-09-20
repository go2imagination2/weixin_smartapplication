# encoding=utf8
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime


class Profile(models.Model):
    """
    用户的补充信息
    """
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = ((GENDER_MALE, '男'), (GENDER_FEMALE, '女'))

    ROLE_STUDENT = 'S'
    ROLE_TEACHER = 'T'
    ROLE_STAFF = 'S'
    ROLE_CHOICES = ((ROLE_STUDENT, '学员'), (ROLE_TEACHER, '讲师'), (ROLE_STAFF, '员工'))

    user = models.OneToOneField(User, unique=True)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_MALE)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    wechat_id = models.CharField(max_length=200, blank=True, null=True)
    create_time = models.DateTimeField(max_length=100, blank=True, null=True, auto_now_add=True)
    update_time = models.DateTimeField(max_length=100, blank=True, null=True)
    nation = models.CharField(max_length=20, blank=True, null=True)
    profession = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    id_card_no = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    membership_card_no = models.CharField(max_length=40, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    @property
    def age(self):
        today_aware = datetime.today()
        return today_aware - self.birthday

    def __unicode__(self):
        return u'%s @ %s' % (self.user.username, self.mobile)


class Entry(models.Model):
    """
    试题
    """
    DIFFICULTY_SUPER = 'S'
    DIFFICULTY_A = 'A'
    DIFFICULTY_B = 'B'
    DIFFICULTY_C = 'C'
    DIFFICULTY_CHOICES = ((DIFFICULTY_SUPER, '超级难'), (DIFFICULTY_A, 'A级'), (DIFFICULTY_B, 'B级'), (DIFFICULTY_C, 'C级'))

    CATEGORY_SINGLE = 'S'
    CATEGORY_MULTI = 'M'
    CATEGORY_FILL_BLANK = 'B'
    CATEGORY_DRAG_DROP = 'D'
    CATEGORY_CHOICES = (
        (CATEGORY_SINGLE, '单选题'), (CATEGORY_MULTI, '多选题'), (CATEGORY_FILL_BLANK, '填空'), (CATEGORY_DRAG_DROP, '拖拽题'))

    question = models.CharField(max_length=250, blank=True, null=True)
    answer = models.CharField(max_length=250, blank=True, null=True, default='')
    role = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_A)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=CATEGORY_SINGLE)
    tips = models.CharField(max_length=250, blank=True, null=True)
    score = models.IntegerField(default=1)

    def __unicode__(self):
        return '[%s]%s' % (self.category, self.question)


class EntryOption(models.Model):
    """
    试题答案选项
    """
    entry = models.ForeignKey(Entry)
    desc = models.CharField(max_length=250, blank=True, null=True)

    def __unicode__(self):
        return '[%s] for Exam %s' % (self.desc, self.entry)

class Paper(models.Model):
    """
    试卷
    """
    name = models.CharField(max_length=50, blank=False, unique=True)
    desc = models.CharField(max_length=2000, blank=False, unique=True)
    image = models.CharField(max_length=100, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    entry = models.ManyToManyField(Entry)

    def __unicode__(self):
        return self.name

    def count(self):
        return len(self.entry.all())


class Exam(models.Model):
    """
    考试
    """
    title = models.CharField(max_length=200, blank=False, unique=True)
    desc = models.CharField(max_length=2000, blank=True, unique=True)
    start_time = models.DateTimeField(max_length=100, blank=True, null=True)
    end_time = models.DateTimeField(max_length=100, blank=True, null=True)
    paper = models.ForeignKey(Paper)

    def __unicode__(self):
        return self.title


class ExamRecord(models.Model):
    """
    单条考试记录
    """
    attendee = models.OneToOneField(User, unique=True)
    exam = models.ForeignKey(Exam)
    answer = models.CharField(max_length=2000, blank=True)
    score = models.CharField(max_length=2000, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s scored %s on %s' % (self.attendee.username, self.score, self.exam)
