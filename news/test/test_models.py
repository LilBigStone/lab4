# from django.test import TestCase
#
#
# from ..models import Profile
#
# class ProfileModelTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         #Set up non-modified objects used by all test methods
#         Profile.objects.create(first_name='Big', last_name='Bob')
#
#     def test_first_name_label(self):
#         profile=Profile.objects.get(id=1)
#         field_label = profile._meta.get_field('first_name').verbose_name
#         self.assertEquals(field_label,'first name')
#
#     def test_date_of_death_label(self):
#         profile=Profile.objects.get(id=1)
#         field_label = profile._meta.get_field('date_of_death').verbose_name
#         self.assertEquals(field_label,'died')
#
#     def test_first_name_max_length(self):
#         profile=Profile.objects.get(id=1)
#         max_length = profile._meta.get_field('first_name').max_length
#         self.assertEquals(max_length,100)
#
#     def test_object_name_is_last_name_comma_first_name(self):
#         profile=Profile.objects.get(id=1)
#         expected_object_name = '%s, %s' % (profile.last_name, profile.first_name)
#         self.assertEquals(expected_object_name,str(profile))
#
#     def test_get_absolute_url(self):
#         profile=Profile.objects.get(id=1)
#         self.assertEquals(profile.get_absolute_url(),'/news/profile/1')
