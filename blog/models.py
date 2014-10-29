from datetime import date

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.management import call_command
from django.dispatch import receiver
from django.http import HttpResponse
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.models import Image
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from south.signals import post_migrate

from blog.utils import export_event

# Home Page
class HomePage(Page):
    body = RichTextField(blank=True)

    indexed_fields = ('body', )

    class Meta:
        verbose_name = "Homepage"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),    
]

HomePage.promote_panels = [
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
]

# Standard page
class StandardPage(Page):    
    body = RichTextField(blank=True)    
    indexed_fields = ('body',  )

StandardPage.content_panels = [
    FieldPanel('title', classname="full title"),      
    FieldPanel('body', classname="full")
    
]

StandardPage.promote_panels = [
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    
]


# Blog index page
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    indexed_fields = ('intro', )

    @property
    def blogs(self):
        # Get list of live blog pages that are descendants of this page
        blogs = BlogPage.objects.live().descendant_of(self)

        # Order by most recent date first
        blogs = blogs.order_by('-date')

        return blogs

    def get_context(self, request):
        # Get blogs
        blogs = self.blogs

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            blogs = blogs.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(blogs, 5)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['blogs'] = blogs
        return context

BlogIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full")    
]

BlogIndexPage.promote_panels = [
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
]


# Blog page
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPage', related_name='tagged_items')


class BlogPage(Page):    
    body = RichTextField()
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    indexed_fields = ('body', )


    @property
    def blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()

    @property
    def get_owner(self):
        return Page.objects.get(pk=self.pk).owner

BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('body', classname="full")    
]

BlogPage.promote_panels = [
    MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]

# Signal handler to load blog data from fixtures after migrations have completed
@receiver(post_migrate)
def import_blog_data(sender, **kwargs):
    # post_migrate will be fired after every app is migrated; we only want to do the import
    # after blog has been migrated
    if kwargs['app'] != 'blog':
        return

    # Check that there isn't already meaningful data in the db that would be clobbered.
    # A freshly created databases should contain no images, tags or snippets
    # and just two page records: root and homepage.
    if Image.objects.count() or Tag.objects.count() or Page.objects.count() > 2:
       return

    # furthermore, if any page has a more specific type than Page, that suggests that meaningful
    # data has been added
    for page in Page.objects.all():
        if page.specific_class != Page:
            return

    import os, shutil
    from django.conf import settings

    fixtures_dir = os.path.join(settings.PROJECT_ROOT, 'blog', 'fixtures')
    fixture_file = os.path.join(fixtures_dir, 'blog.json')
    image_src_dir = os.path.join(fixtures_dir, 'images')
    image_dest_dir = os.path.join(settings.MEDIA_ROOT, 'original_images')

    call_command('loaddata', fixture_file, verbosity=0)

    if not os.path.isdir(image_dest_dir):
        os.makedirs(image_dest_dir)

    for filename in os.listdir(image_src_dir):
        shutil.copy(os.path.join(image_src_dir, filename), image_dest_dir)
