from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from .models import User, Post, Group, Follow, Comment


class TestFinalTask6Sprint(TestCase):
    def setUp(self):
        self.client = Client()
        self.client2 = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345")
        self.user_clone = User.objects.create_user(
            username="sarah_clone", email="connor_clone.s@skynet.com", password="12345")
        self.client_auth = Client()
        self.client_auth.force_login(self.user_clone)
        self.client_auth.post(reverse('new_post'), data={
                              'text': 'test_text'}, follow=True)
        self.client.force_login(self.user)
        self.client.post(reverse('new_post'), data={
            'text': 'test_text'}, follow=True)
        self.url_comment = reverse('post', kwargs={
            'post_id': 1, 'username': self.user_clone.username})
        self.url_add_comment = reverse('add_comment', kwargs={
            'post_id': 1, 'username': self.user_clone.username})

    def test_CRUD_follow(self):
        self.assertEqual(Follow.objects.count(), 0)
        url = reverse('profile_follow', kwargs={
                      'username': self.user.username})
        self.client_auth.get(url, follow=True)
        self.assertEqual(Follow.objects.count(), 1)
        url = reverse('profile_unfollow', kwargs={
            'username': self.user.username})
        self.client_auth.get(url, follow=True)
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_menu_not_follow(self):
        # проверка на наличие постов у неподписанного юзера
        response = self.client_auth.get(reverse('follow_index'))
        self.assertEqual(Follow.objects.count(), 0)
        self.assertEqual(response.context['paginator'].count, 0)

    def test_new_post_menu_follow(self):
        # проверка на наличие постов у подписанного юзера
        url = reverse('profile_follow', kwargs={
            'username': self.user.username})
        self.client_auth.get(url, follow=True)
        self.assertEqual(Follow.objects.count(), 1)
        response = self.client_auth.get(reverse('follow_index'))
        self.assertEqual(response.context['paginator'].count, 1)

    def test_new_comment_auth(self):
        self.client_auth.post(
            self.url_add_comment, data={'text': 'test_comment_text'}, follow=True)
        response_get = self.client.get(self.url_comment)
        self.assertEqual(response_get.context['comments'].count(), 1)

    def test_new_comment_not_auth(self):
        self.client.logout()
        self.client.post(self.url_add_comment, data={
                         'text': 'test_comment_text2'}, follow=True)
        response_get = self.client.get(self.url_comment)
        self.assertEqual(response_get.context['comments'].count(), 0)


class TestNewfunctionalof6Sprint(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345")
        self.group = Group.objects.create(
            title='GroupTestTitle',
            description='GroupDescriptionTest',
            slug='testSlug')
        self.client_auth = Client()
        self.client_auth.force_login(self.user)
        self.client_auth.post(reverse('new_post'), data={
                              'text': 'test_text'}, follow=True)

    def test_404_template(self):
        url = reverse('profile', kwargs={'username': 'dontexisturl'})
        response = self.client_auth.get(url)
        self.assertEqual(response.status_code, 404)

    def test_img_in_post_page(self):
        text = 'post with image'
        with open('posts/file.jpg', 'rb') as img:
            self.client_auth.post(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}), data={
                                  'author': self.user, 'text': text, 'image': img}, follow=True)
            response = self.client_auth.get(
                reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))
            self.assertContains(response, '<img class="card-img"', count=None,
                                status_code=200, msg_prefix='Не найти картинку мне')

    def test_img_in_other_pages(self):
        text = 'post with image'
        url_list = [reverse('index'),
                    reverse('profile', kwargs={
                            'username': self.user.username}),
                    reverse('group', kwargs={'slug': self.group.slug})]
        with open('posts/file.jpg', 'rb') as img:
            self.client_auth.post(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}), data={
                                  'author': self.user, 'text': text, 'image': img, 'group': self.group.pk}, follow=True)
            cache.clear()
            for url in url_list:
                response = self.client_auth.get(url)
                self.assertContains(response, '<img class="card-img"',
                                    status_code=200, msg_prefix='Не найти картинку мне')

    def test_non_graph_file(self):
        with open('posts/file.docx', 'rb') as img:
            response = self.client_auth.post(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}), data={
                'author': self.user, 'text': 'text321', 'image': img}, follow=True)
            error_text = 'Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.'
            self.assertFormError(response, 'form', 'image', error_text)

    def test_cache_index(self):
        response = self.client_auth.get(reverse('index'))
        self.client_auth.post(reverse('new_post'), data={
            'text': 'test_text2222'}, follow=True)
        self.assertEqual(response.context['paginator'].count, 1)
        cache.clear()
        response = self.client_auth.get(reverse('index'))
        self.assertEqual(response.context['paginator'].count, 2)


class TestNewfunctionalof5Sprint(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345")
        self.client_auth = Client()
        self.client_auth.force_login(self.user)
        self.url_list = [reverse('index'),
                         reverse('profile', kwargs={
                                 'username': self.user.username}),
                         reverse('post', kwargs={'username': self.user.username,
                                                 'post_id': 1})]
        self.test_text = 'TestTextFromConsole'
        self.test_text_new = 'NewTestTextFromConsole'
        self.new_post_url = reverse('new_post')

    def check_post_on_page(self, text):
        for url in self.url_list:
            response_get = self.client.get(url)
            if 'paginator' in response_get.context:
                self.assertEqual(response_get.context['paginator'].count, 1)
                self.assertEqual(
                    response_get.context['page'][0].text, text)
            else:
                self.assertEqual(
                    response_get.context['post'].text, text)

    def test_page_create(self):
        url = reverse('profile', kwargs={'username': 'sarah'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_can_published(self):
        # Авторизованный пользователь может опубликовать пост (new)
        response = self.client_auth.get(self.new_post_url)
        self.assertEqual(response.status_code, 200)

    def test_cant_publ(self):
        # Неавторизованный посетитель не может опубликовать пост
        # (его редиректит на страницу входа)
        response = self.client.get(self.new_post_url)
        expected_url = reverse('login') + f'?next={self.new_post_url}'
        self.assertRedirects(response, expected_url, status_code=302,
                             target_status_code=200, fetch_redirect_response=True)

    def test_post_creation(self):
        # После публикации поста новая запись появляется на главной странице сайта (index),
        # на персональной странице пользователя (profile), и на отдельной странице поста (post)
        self.client_auth.post(
            self.new_post_url,
            data={'text': self.test_text},
            follow=True)
        self.check_post_on_page(self.test_text)

    def test_post_edition(self):
        self.client_auth.post(self.new_post_url, data={
                              'text': self.test_text}, follow=True)
        self.client_auth.post(reverse('post_edit', kwargs={
                                      'username': self.user.username,
                                      'post_id': 1}),
                              data={'text': self.test_text_new}, follow=True)
        self.check_post_on_page(self.test_text_new)
