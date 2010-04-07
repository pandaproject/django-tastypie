import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from tastypie import fields
from tastypie.representations.simple import Representation
from tastypie.representations.models import ModelRepresentation
from core.models import Note, Subject


class TestObject(object):
    name = None
    view_count = None
    date_joined = None


class BasicRepresentation(Representation):
    name = fields.CharField(attribute='name')
    view_count = fields.IntegerField(attribute='view_count', default=0)
    date_joined = fields.DateTimeField(null=True)
    
    class Meta:
        object_class = TestObject
    
    def dehydrate_date_joined(self, obj):
        if getattr(obj, 'date_joined', None) is not None:
            return obj.date_joined
        
        if self.date_joined.value is not None:
            return self.date_joined.value
        
        return datetime.datetime(2010, 3, 27, 22, 30, 0)
    
    def hydrate_date_joined(self):
        self.instance.date_joined = self.date_joined.value


class AnotherBasicRepresentation(BasicRepresentation):
    date_joined = fields.DateField(attribute='created')
    is_active = fields.BooleanField(attribute='is_active', default=True)


class RepresentationTestCase(TestCase):
    def test_fields(self):
        basic = BasicRepresentation()
        self.assertEqual(len(basic.fields), 3)
        self.assert_('name' in basic.fields)
        self.assertEqual(isinstance(basic.name, fields.CharField), True)
        self.assert_('view_count' in basic.fields)
        self.assertEqual(isinstance(basic.view_count, fields.IntegerField), True)
        self.assert_('date_joined' in basic.fields)
        self.assertEqual(isinstance(basic.date_joined, fields.DateTimeField), True)
        
        another = AnotherBasicRepresentation()
        self.assertEqual(len(another.fields), 4)
        self.assert_('name' in another.fields)
        self.assertEqual(isinstance(another.name, fields.CharField), True)
        self.assert_('view_count' in another.fields)
        self.assertEqual(isinstance(another.view_count, fields.IntegerField), True)
        self.assert_('date_joined' in another.fields)
        self.assertEqual(isinstance(another.date_joined, fields.DateField), True)
        self.assert_('is_active' in another.fields)
        self.assertEqual(isinstance(another.is_active, fields.BooleanField), True)
    
    def test_full_dehydrate(self):
        test_object_1 = TestObject()
        test_object_1.name = 'Daniel'
        test_object_1.view_count = 12
        test_object_1.date_joined = datetime.datetime(2010, 3, 30, 9, 0, 0)
        test_object_1.foo = "Hi, I'm ignored."
        
        basic = BasicRepresentation()
        
        # Sanity check.
        self.assertEqual(basic.name.value, None)
        self.assertEqual(basic.view_count.value, None)
        self.assertEqual(basic.date_joined.value, None)
        
        basic.full_dehydrate(test_object_1)
        self.assertEqual(basic.name.value, 'Daniel')
        self.assertEqual(basic.view_count.value, 12)
        self.assertEqual(basic.date_joined.value.year, 2010)
        self.assertEqual(basic.date_joined.value.day, 30)
        
        # Now check the fallback behaviors.
        test_object_2 = TestObject()
        test_object_2.name = 'Daniel'
        basic_2 = BasicRepresentation()
        
        # Sanity check.
        self.assertEqual(basic_2.name.value, None)
        self.assertEqual(basic_2.view_count.value, None)
        self.assertEqual(basic_2.date_joined.value, None)
        
        basic_2.full_dehydrate(test_object_2)
        self.assertEqual(basic_2.name.value, 'Daniel')
        self.assertEqual(basic_2.view_count.value, 0)
        self.assertEqual(basic_2.date_joined.value.year, 2010)
        self.assertEqual(basic_2.date_joined.value.day, 27)
        
        test_object_3 = TestObject()
        test_object_3.name = 'Joe'
        test_object_3.view_count = 5
        test_object_3.created = datetime.datetime(2010, 3, 29, 11, 0, 0)
        test_object_3.is_active = False
        another_1 = AnotherBasicRepresentation()
        
        # Sanity check.
        self.assertEqual(another_1.name.value, None)
        self.assertEqual(another_1.view_count.value, None)
        self.assertEqual(another_1.date_joined.value, None)
        self.assertEqual(another_1.is_active.value, None)
        
        another_1.full_dehydrate(test_object_3)
        self.assertEqual(another_1.name.value, 'Joe')
        self.assertEqual(another_1.view_count.value, 5)
        self.assertEqual(another_1.date_joined.value.year, 2010)
        self.assertEqual(another_1.date_joined.value.day, 29)
        self.assertEqual(another_1.is_active.value, False)
    
    def test_full_hydrate(self):
        basic = BasicRepresentation()
        
        # Sanity check.
        self.assertEqual(basic.name.value, None)
        self.assertEqual(basic.view_count.value, None)
        self.assertEqual(basic.date_joined.value, None)
        
        basic = BasicRepresentation(data={
            'name': 'Daniel',
            'view_count': 6,
            'date_joined': datetime.datetime(2010, 2, 15, 12, 0, 0)
        })
        
        # Sanity check.
        self.assertEqual(basic.name.value, 'Daniel')
        self.assertEqual(basic.view_count.value, 6)
        self.assertEqual(basic.date_joined.value, datetime.datetime(2010, 2, 15, 12, 0, 0))
        self.assertEqual(basic.instance, None)
        
        # Now load up the data.
        basic.full_hydrate()
        
        self.assertEqual(basic.name.value, 'Daniel')
        self.assertEqual(basic.view_count.value, 6)
        self.assertEqual(basic.date_joined.value, datetime.datetime(2010, 2, 15, 12, 0, 0))
        self.assertEqual(basic.instance.name, 'Daniel')
        self.assertEqual(basic.instance.view_count, 6)
        self.assertEqual(basic.instance.date_joined, datetime.datetime(2010, 2, 15, 12, 0, 0))
    
    def test_get_list(self):
        self.assertRaises(NotImplementedError, BasicRepresentation.get_list)
    
    def test_get(self):
        basic = BasicRepresentation()
        self.assertRaises(NotImplementedError, basic.get, obj_id=1)
    
    def test_create(self):
        basic = BasicRepresentation()
        self.assertRaises(NotImplementedError, basic.create)
    
    def test_update(self):
        basic = BasicRepresentation()
        self.assertRaises(NotImplementedError, basic.update)
    
    def test_delete(self):
        basic = BasicRepresentation()
        self.assertRaises(NotImplementedError, basic.delete)


class NoteRepresentation(ModelRepresentation):
    class Meta:
        queryset = Note.objects.filter(is_active=True)


class CustomNoteRepresentation(ModelRepresentation):
    author = fields.CharField(attribute='author__username')
    constant = fields.IntegerField(default=20)
    
    class Meta:
        queryset = Note.objects.all()
        fields = ['title', 'content', 'created', 'is_active']


class UserRepresentation(ModelRepresentation):
    class Meta:
        queryset = User.objects.all()


class SubjectRepresentation(ModelRepresentation):
    class Meta:
        queryset = Subject.objects.all()


class RelatedNoteRepresentation(ModelRepresentation):
    author = fields.ForeignKey(UserRepresentation, 'author')
    subjects = fields.ManyToManyField(SubjectRepresentation, 'subjects')
    
    class Meta:
        queryset = Note.objects.all()
        fields = ['title', 'content', 'created', 'is_active']


class ModelRepresentationTestCase(TestCase):
    fixtures = ['note_testdata.json']
    urls = 'core.tests.field_urls'
    
    def setUp(self):
        super(ModelRepresentationTestCase, self).setUp()
        self.note_1 = Note.objects.get(pk=1)
        self.subject_1 = Subject.objects.create(
            name='News',
            url='/news/'
        )
        self.subject_2 = Subject.objects.create(
            name='Photos',
            url='/photos/'
        )
        self.note_1.subjects.add(self.subject_1)
        self.note_1.subjects.add(self.subject_2)
    
    def test_configuration(self):
        note = NoteRepresentation()
        # FIXME: Once relations are in, this number ought to go up.
        self.assertEqual(len(note.fields), 6)
        self.assertEqual(sorted(note.fields.keys()), ['content', 'created', 'is_active', 'slug', 'title', 'updated'])
        
        custom = CustomNoteRepresentation()
        self.assertEqual(len(custom.fields), 6)
        self.assertEqual(sorted(custom.fields.keys()), ['author', 'constant', 'content', 'created', 'is_active', 'title'])
    
    def test_get_list(self):
        notes = NoteRepresentation.get_list()
        self.assertEqual(len(notes), 4)
        self.assertEqual(notes[0].is_active.value, True)
        self.assertEqual(notes[0].title.value, u'First Post!')
        self.assertEqual(notes[1].is_active.value, True)
        self.assertEqual(notes[1].title.value, u'Another Post')
        self.assertEqual(notes[2].is_active.value, True)
        self.assertEqual(notes[2].title.value, u'Recent Volcanic Activity.')
        self.assertEqual(notes[3].is_active.value, True)
        self.assertEqual(notes[3].title.value, u"Granny's Gone")
        
        customs = CustomNoteRepresentation.get_list()
        self.assertEqual(len(customs), 6)
        self.assertEqual(customs[0].is_active.value, True)
        self.assertEqual(customs[0].title.value, u'First Post!')
        self.assertEqual(customs[0].author.value, u'johndoe')
        self.assertEqual(customs[0].constant.value, 20)
        self.assertEqual(customs[1].is_active.value, True)
        self.assertEqual(customs[1].title.value, u'Another Post')
        self.assertEqual(customs[1].author.value, u'johndoe')
        self.assertEqual(customs[1].constant.value, 20)
        self.assertEqual(customs[2].is_active.value, False)
        self.assertEqual(customs[2].title.value, u'Hello World!')
        self.assertEqual(customs[2].author.value, u'janedoe')
        self.assertEqual(customs[3].is_active.value, True)
        self.assertEqual(customs[3].title.value, u'Recent Volcanic Activity.')
        self.assertEqual(customs[3].author.value, u'janedoe')
        self.assertEqual(customs[4].is_active.value, False)
        self.assertEqual(customs[4].title.value, u'My favorite new show')
        self.assertEqual(customs[4].author.value, u'johndoe')
        self.assertEqual(customs[5].is_active.value, True)
        self.assertEqual(customs[5].title.value, u"Granny's Gone")
        self.assertEqual(customs[5].author.value, u'janedoe')
    
    def test_get(self):
        note = NoteRepresentation()
        note.get(pk=1)
        self.assertEqual(note.content.value, u'This is my very first post using my shiny new API. Pretty sweet, huh?')
        self.assertEqual(note.created.value, datetime.datetime(2010, 3, 30, 20, 5))
        self.assertEqual(note.is_active.value, True)
        self.assertEqual(note.slug.value, u'first-post')
        self.assertEqual(note.title.value, u'First Post!')
        self.assertEqual(note.updated.value, datetime.datetime(2010, 3, 30, 20, 5))
        
        custom = CustomNoteRepresentation()
        custom.get(pk=1)
        self.assertEqual(custom.content.value, u'This is my very first post using my shiny new API. Pretty sweet, huh?')
        self.assertEqual(custom.created.value, datetime.datetime(2010, 3, 30, 20, 5))
        self.assertEqual(custom.is_active.value, True)
        self.assertEqual(custom.author.value, u'johndoe')
        self.assertEqual(custom.title.value, u'First Post!')
        self.assertEqual(custom.constant.value, 20)
        
        related = RelatedNoteRepresentation(api_name='v1', resource_name='notes')
        related.get(pk=1)
        self.assertEqual(related.content.value, u'This is my very first post using my shiny new API. Pretty sweet, huh?')
        self.assertEqual(related.created.value, datetime.datetime(2010, 3, 30, 20, 5))
        self.assertEqual(related.is_active.value, True)
        self.assertEqual(related.author.value, '/api/v1/users/1/')
        self.assertEqual(related.title.value, u'First Post!')
        self.assertEqual(related.subjects.value, ['/api/v1/subjects/1/', '/api/v1/subjects/2/'])
    
    def test_create(self):
        self.assertEqual(Note.objects.all().count(), 6)
        note = NoteRepresentation(data={
            'title': "A new post!",
            'slug': "a-new-post",
            'content': "Testing, 1, 2, 3!",
            'is_active': True
        })
        note.create()
        self.assertEqual(Note.objects.all().count(), 7)
        latest = Note.objects.get(slug='a-new-post')
        self.assertEqual(latest.title, u"A new post!")
        self.assertEqual(latest.slug, u'a-new-post')
        self.assertEqual(latest.content, u'Testing, 1, 2, 3!')
        self.assertEqual(latest.is_active, True)
        
        note = RelatedNoteRepresentation(data={
            'title': "Yet another new post!",
            'slug': "yet-another-new-post",
            'content': "WHEEEEEE!",
            'is_active': True,
            'author': '/api/v1/users/1/',
            'subjects': ['/api/v1/subjects/2/'],
        })
        note.create()
        self.assertEqual(Note.objects.all().count(), 8)
        latest = Note.objects.get(slug='yet-another-new-post')
        self.assertEqual(latest.title, u"Yet another new post!")
        self.assertEqual(latest.slug, u'yet-another-new-post')
        self.assertEqual(latest.content, u'WHEEEEEE!')
        self.assertEqual(latest.is_active, True)
        self.assertEqual(latest.author.username, True)
        self.assertEqual(latest.subjects.all().count(), True)
    
    def test_update(self):
        self.assertEqual(Note.objects.all().count(), 6)
        note = NoteRepresentation()
        note.get(pk=1)
        note.title.value = 'Whee!'
        note.update(pk=1)
        self.assertEqual(Note.objects.all().count(), 6)
        numero_uno = Note.objects.get(pk=1)
        self.assertEqual(numero_uno.title, u'Whee!')
        self.assertEqual(numero_uno.slug, u'first-post')
        self.assertEqual(numero_uno.content, u'This is my very first post using my shiny new API. Pretty sweet, huh?')
        self.assertEqual(numero_uno.is_active, True)
    
    def test_delete(self):
        self.assertEqual(Note.objects.all().count(), 6)
        note = NoteRepresentation()
        note.delete(pk=1)
        self.assertEqual(Note.objects.all().count(), 5)
        self.assertRaises(Note.DoesNotExist, Note.objects.get, pk=1)
