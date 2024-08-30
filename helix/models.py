from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class Control(models.Model):
    class StatusChoices(models.TextChoices):
        DRAFT = 'Draft', _('Draft')
        IN_REVIEW = 'In Review', _('In Review')
        APPROVED = 'Approved', _('Approved')
        DEPRECATED = 'Deprecated', _('Deprecated')

    class PriorityChoices(models.IntegerChoices):
        HIGH = 1, _('High')
        MEDIUM = 2, _('Medium')
        LOW = 3, _('Low')

    class NiceRoleChoices(models.TextChoices):
        SECURELY_PROVISION = 'Securely Provision', _('Securely Provision')
        OPERATE_AND_MAINTAIN = 'Operate and Maintain', _('Operate and Maintain')
        OVERSEE_AND_GOVERN = 'Oversee and Govern', _('Oversee and Govern')
        PROTECT_AND_DEFEND = 'Protect and Defend', _('Protect and Defend')
        ANALYZE = 'Analyze', _('Analyze')
        COLLECT_AND_OPERATE = 'Collect and Operate', _('Collect and Operate')
        INVESTIGATE = 'Investigate', _('Investigate')

    class DetectionChoices(models.TextChoices):
        ATOMIC = 'Atomic', _('Atomic')
        BEHAVIORAL_ATOMIC = 'Behavioral, Atomic', _('Behavioral, Atomic')
        STATISTICAL = 'Statistical', _('Statistical')

    class SignalsChoices(models.TextChoices):
        BAGGAGE = 'Baggage', _('Baggage')
        TRACES = 'Traces', _('Traces')

    class ComponentsChoices(models.TextChoices):
        DATA = 'Data', _('Data')
        SDK = 'SDK', _('SDK')

    class SpanChoices(models.TextChoices):
        UNSET = 'Unset', _('Unset')
        DATA = 'Data', _('Data')

    class MetricChoices(models.TextChoices):
        COUNTER = 'Counter', _('Counter')
        MEASURE = 'Measure', _('Measure')
        OBSERVER = 'Observer', _('Observer')

    class Meta:
        verbose_name = _('Control')
        verbose_name_plural = _('Controls')
        indexes = [
            models.Index(fields=['control_short_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['last_updated'])
        ]

    def __str__(self):
        return f"{self.control_short_number} - {self.name}"

    name = models.CharField(_('Name'), max_length=255)
    control_short_number = models.CharField(_('Short Number'), max_length=50, unique=True, db_index=True)
    description = models.TextField(_('Description'))
    tags = models.JSONField(_('Tags'), help_text=_("List of tags related to the control."))

    status = models.CharField(_('Status'), max_length=50, choices=StatusChoices.choices)
    priority = models.PositiveSmallIntegerField(_('Priority'), choices=PriorityChoices.choices, help_text=_("Priority level"))
    selected = models.BooleanField(_('Selected'), default=False)
    last_updated = models.DateTimeField(_('Last Updated'), auto_now=True)

    project_timeline_start = models.DateField(_('Project Timeline Start'))
    project_timeline_end = models.DateField(_('Project Timeline End'))
    responsible_team = models.CharField(_('Responsible Team'), max_length=255)
    team_members = models.ManyToManyField(User, blank=True, related_name='control_team_members')

    exception_required = models.BooleanField(_('Exception Required'), default=False)
    exception_for = models.TextField(_('Exception For'), blank=True, null=True)
    exception_duration_start = models.DateField(_('Exception Duration Start'), blank=True, null=True)
    exception_duration_end = models.DateField(_('Exception Duration End'), blank=True, null=True)

    csf_function = models.CharField(_('CSF Function'), max_length=50, choices=[
        ('Identify', 'Identify'),
        ('Protect', 'Protect'),
        ('Detect', 'Detect'),
        ('Respond', 'Respond'),
        ('Recover', 'Recover')
    ], help_text=_("NIST CSF core function this control supports."))
    csf_category = models.CharField(_('CSF Category'), max_length=50, help_text=_("NIST CSF category (e.g., ID.AM, PR.AC)"))

    responsible = models.CharField(_('Responsible Role'), max_length=50, choices=NiceRoleChoices.choices, help_text=_("Role responsible for the control."))
    accountable = models.CharField(_('Accountable Role'), max_length=50, choices=NiceRoleChoices.choices, help_text=_("Role accountable for the control."))
    consulted = models.CharField(_('Consulted Role'), max_length=50, choices=NiceRoleChoices.choices, help_text=_("Role consulted for the control."))
    informed = models.CharField(_('Informed Role'), max_length=50, choices=NiceRoleChoices.choices, help_text=_("Role informed about the control."))

    visibility = models.CharField(_('Visibility'), max_length=255)
    alerting = models.CharField(_('Alerting'), max_length=255)
    detection = models.CharField(_('Detection'), max_length=255, choices=DetectionChoices.choices)
    telemetry = models.CharField(_('Telemetry'), max_length=255)
    signals = models.CharField(_('Signals'), max_length=255, choices=SignalsChoices.choices)

    components = models.JSONField(_('Components'), help_text=_("List of components covered by this control."))
    span = models.CharField(_('Span'), max_length=255, choices=SpanChoices.choices, help_text=_("The span of control (e.g., organization-wide, departmental)"))
    metric = models.CharField(_('Metric'), max_length=255, choices=MetricChoices.choices, help_text=_("Metric used to measure control effectiveness"))
    report = models.TextField(_('Report'), help_text=_("Details on how the control's effectiveness is reported"))

    discussion = models.TextField(_('Discussion'))

    related_controls = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='related_by')

    files = models.FileField(_('Files'), upload_to='control_files/', blank=True, null=True)

    @property
    def get_absolute_url(self):
        return reverse('control_detail', kwargs={'pk': self.pk})

class ControlSubitem(models.Model):
    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name='subitems')
    subitem = models.JSONField(_('Subitem Details'), help_text=_("Structured subitem details"))

    def __str__(self):
        return f"Subitem for {self.control.name}"

class ControlFile(models.Model):
    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name='control_files')
    file = models.FileField(_('File'), upload_to='control_files/')
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)

    def __str__(self):
        return f"File for {self.control.name} uploaded on {self.uploaded_at}"

# Custom manager for Control model
class ControlManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'team_members',
            'related_controls',
            'files'
        )

    def active_controls(self):
        return self.get_queryset().filter(status__in=[Control.StatusChoices.APPROVED, _('Active')])

    def draft_controls(self):
        return self.get_queryset().filter(status=Control.StatusChoices.DRAFT)

# Apply the custom manager to the Control model
Control.objects = ControlManager()