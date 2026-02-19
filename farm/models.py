from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta, date

class Goat(models.Model):
    """मुख्य बकरी मॉडल - Main Goat Model"""
    BREED_CHOICES = [
        # International Breeds
        ('boer', 'Boer'),
        ('saanen', 'Saanen'),
        ('alpine', 'Alpine'),
        ('nubian', 'Nubian'),
        ('anglo_nubian', 'Anglo-Nubian'),
        ('toggeneburg', 'Toggeneburg'),
        ('chamois_colored', 'Chamois Colored'),
        ('oberhasli', 'Oberhasli'),
        # Indian Breeds (भारतीय नस्लें)
        ('sirohi', 'Sirohi (सिरोही)'),
        ('barbari', 'Barbari (बरबरी)'),
        ('jamunapari', 'Jamunapari (जमुनापारी)'),
        ('beetal', 'Beetal (बीटल)'),
        ('osmanabadi', 'Osmanabadi (उस्मानाबादी)'),
        ('marwari', 'Marwari (मारवाड़ी)'),
        ('kutchi', 'Kutchi (कच्छी)'),
        ('zalawadi', 'Zalawadi (झालावाड़ी)'),
        ('ganjam', 'Ganjam (गंजाम)'),
        ('local', 'Local/Desi (देसी)'),
    ]
    
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    STATUS_CHOICES = [('A', 'Active'), ('P', 'Pregnant'), ('S', 'Sold'), ('D', 'Dead')]
    
    tag_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=20, choices=BREED_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    color = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    weight = models.FloatField(validators=[MinValueValidator(0)])
    # FIX #1: Proper ImageField — admin ke saath compatible, Pillow required
    photo = models.ImageField(upload_to='goats/', null=True, blank=True)
    purchase_date = models.DateField()
    purchase_price = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    mother = models.ForeignKey('self', null=True, blank=True, related_name='kids_as_mother', on_delete=models.SET_NULL)
    father = models.ForeignKey('self', null=True, blank=True, related_name='kids_as_father', on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, help_text='Additional notes about this goat / बकरी के बारे में अतिरिक्त नोट्स')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tag_number} - {self.name}"

    def is_male(self):
        return self.gender == 'M'

    def is_female(self):
        return self.gender == 'F'

    def get_age_months(self):
        today = date.today()
        months = (today.year - self.date_of_birth.year) * 12 + (today.month - self.date_of_birth.month)
        return max(0, months)

    def get_age_years(self):
        return self.get_age_months() // 12

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Goats (बकरियां)"


class BreedingRecord(models.Model):
    """प्रजनन रिकॉर्ड - Breeding Records"""
    STATUS_CHOICES = [('P', 'Pending'), ('C', 'Confirmed'), ('F', 'Failed'), ('D', 'Delivered')]
    
    mother = models.ForeignKey(Goat, related_name='breeding_as_mother', on_delete=models.CASCADE)
    father = models.ForeignKey(Goat, related_name='breeding_as_father', on_delete=models.CASCADE)
    breeding_date = models.DateField()
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    number_of_kids = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # FIX: self.mother / self.father access se extra DB query hoti thi
        # values_list se sirf gender field fetch karo — efficient
        if self.mother_id:
            mother_gender = Goat.objects.filter(pk=self.mother_id).values_list('gender', flat=True).first()
            if mother_gender and mother_gender != 'F':
                raise ValidationError({'mother': 'Mother must be a female goat (Gender=F).'})
        if self.father_id:
            father_gender = Goat.objects.filter(pk=self.father_id).values_list('gender', flat=True).first()
            if father_gender and father_gender != 'M':
                raise ValidationError({'father': 'Father must be a male goat (Gender=M).'})
        if self.mother_id and self.father_id and self.mother_id == self.father_id:
            raise ValidationError('Mother and Father cannot be the same goat.')

    def save(self, *args, **kwargs):
        self.full_clean()
        # Auto-calculate expected delivery date (goat gestation ≈ 150 days)
        if not self.expected_delivery_date and self.breeding_date:
            self.expected_delivery_date = self.breeding_date + timedelta(days=150)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mother.name} x {self.father.name} - {self.breeding_date}"

    class Meta:
        verbose_name_plural = "Breeding Records (प्रजनन रिकॉर्ड)"


class HealthRecord(models.Model):
    """स्वास्थ्य रिकॉर्ड - Health Records"""
    RECORD_TYPE_CHOICES = [
        ('V', 'Vaccination'),
        ('D', 'Deworming'),
        ('T', 'Treatment'),
        ('C', 'Checkup'),
        ('S', 'Surgery'),
    ]
    
    goat = models.ForeignKey(Goat, related_name='health_records', on_delete=models.CASCADE)
    record_type = models.CharField(max_length=1, choices=RECORD_TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField()
    medicine_used = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    cost = models.FloatField(validators=[MinValueValidator(0)])
    veterinarian = models.CharField(max_length=100, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goat.name} - {self.get_record_type_display()}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Health Records (स्वास्थ्य रिकॉर्ड)"


class MilkProduction(models.Model):
    """दूध उत्पादन - Milk Production"""
    SESSION_CHOICES = [('M', 'Morning'), ('E', 'Evening')]
    
    goat = models.ForeignKey(Goat, related_name='milk_records', on_delete=models.CASCADE)
    date = models.DateField()
    session = models.CharField(max_length=1, choices=SESSION_CHOICES)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    fat_percentage = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goat.name} - {self.date} ({self.get_session_display()}) {self.quantity}L"

    class Meta:
        ordering = ['-date']
        unique_together = ['goat', 'date', 'session']
        verbose_name_plural = "Milk Production (दूध उत्पादन)"


class FeedInventory(models.Model):
    """चारा इन्वेंटरी - Feed Inventory"""
    FEED_TYPE_CHOICES = [
        ('G', 'Green Feed'),
        ('D', 'Dry Feed'),
        ('C', 'Concentrate'),
        ('H', 'Hay'),
        ('S', 'Supplement'),
    ]
    
    feed_name = models.CharField(max_length=100)
    feed_type = models.CharField(max_length=1, choices=FEED_TYPE_CHOICES)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='kg')
    unit_price = models.FloatField(validators=[MinValueValidator(0)])
    purchase_date = models.DateField()
    supplier = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_cost(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.feed_name} - {self.quantity} {self.unit}"

    class Meta:
        verbose_name_plural = "Feed Inventory (चारा इन्वेंटरी)"


class FeedConsumption(models.Model):
    """चारा खपत - Feed Consumption"""
    date = models.DateField()
    feed = models.ForeignKey(FeedInventory, related_name='consumption', on_delete=models.CASCADE)
    quantity_consumed = models.FloatField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        if not self.pk:
            # NEW record: stock check karo aur deduct karo
            feed = FeedInventory.objects.get(pk=self.feed_id)
            if self.quantity_consumed > feed.quantity:
                raise ValidationError(
                    f"Insufficient stock: available {feed.quantity} {feed.unit}, "
                    f"requested {self.quantity_consumed} {feed.unit}"
                )
            FeedInventory.objects.filter(pk=self.feed_id).update(
                quantity=models.F('quantity') - self.quantity_consumed
            )
        else:
            # EDIT: purana record fetch karo, difference adjust karo
            old_record = FeedConsumption.objects.get(pk=self.pk)
            diff = self.quantity_consumed - old_record.quantity_consumed
            if diff != 0:
                feed = FeedInventory.objects.get(pk=self.feed_id)
                if diff > 0 and diff > feed.quantity:
                    raise ValidationError(
                        f"Insufficient stock: available {feed.quantity} {feed.unit}, "
                        f"additional requested {diff} {feed.unit}"
                    )
                FeedInventory.objects.filter(pk=self.feed_id).update(
                    quantity=models.F('quantity') - diff
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.feed.feed_name} - {self.date} ({self.quantity_consumed} {self.feed.unit})"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Feed Consumption (चारा खपत)"


class Sale(models.Model):
    """बिक्रय - Sales"""
    SALE_TYPE_CHOICES = [
        ('G', 'Goat'),
        ('M', 'Milk'),
        ('MN', 'Manure'),
        ('O', 'Other'),
    ]
    PAYMENT_STATUS_CHOICES = [('P', 'Paid'), ('UP', 'Unpaid'), ('PA', 'Partial')]
    
    sale_type = models.CharField(max_length=2, choices=SALE_TYPE_CHOICES)
    goat = models.ForeignKey(Goat, null=True, blank=True, related_name='sales', on_delete=models.SET_NULL)
    date = models.DateField()
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20)
    price_per_unit = models.FloatField(validators=[MinValueValidator(0)])
    total_amount = models.FloatField(validators=[MinValueValidator(0)])
    buyer_name = models.CharField(max_length=100)
    buyer_contact = models.CharField(max_length=20, blank=True)
    payment_status = models.CharField(max_length=2, choices=PAYMENT_STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total_amount from quantity × price_per_unit
        self.total_amount = round(self.quantity * self.price_per_unit, 2)
        super().save(*args, **kwargs)
        # Auto-update goat status to 'S' (Sold) when a goat sale is recorded
        if self.sale_type == 'G' and self.goat and self.goat.status != 'S':
            Goat.objects.filter(pk=self.goat_id).update(status='S')

    def __str__(self):
        return f"{self.get_sale_type_display()} - {self.total_amount}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Sales (बिक्रय)"


class Expense(models.Model):
    """खर्च - Expenses"""
    EXPENSE_TYPE_CHOICES = [
        ('F', 'Feed'),
        ('M', 'Medicine'),
        ('V', 'Veterinary'),
        ('R', 'Repairs'),
        ('U', 'Utilities'),
        ('L', 'Labour'),
        ('O', 'Other'),
    ]
    # FIX #2: Duplicate 'C' key hataya — Cheque ke liye 'CH' use kiya
    PAYMENT_METHOD_CHOICES = [
        ('C', 'Cash'),
        ('B', 'Bank Transfer'),
        ('CH', 'Cheque'),
        ('O', 'Online/UPI'),
    ]
    
    date = models.DateField()
    expense_type = models.CharField(max_length=1, choices=EXPENSE_TYPE_CHOICES)
    description = models.TextField()
    amount = models.FloatField(validators=[MinValueValidator(0)])
    paid_to = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES, default='C')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.amount}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Expenses (खर्च)"


class WeightRecord(models.Model):
    """वजन रिकॉर्ड - Weight Records"""
    goat = models.ForeignKey(Goat, related_name='weight_records', on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goat.name} - {self.date}: {self.weight} kg"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Weight Records (वजन रिकॉर्ड)"


class Task(models.Model):
    """कार्य प्रबंधन - Task Management"""
    STATUS_CHOICES = [('P', 'Pending'), ('IP', 'In Progress'), ('C', 'Completed')]
    PRIORITY_CHOICES = [('H', 'High'), ('M', 'Medium'), ('L', 'Low')]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='P')
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    due_date = models.DateField()
    assigned_to = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title} — {self.get_status_display()}"

    class Meta:
        ordering = ['-due_date']
        verbose_name_plural = "Tasks (कार्य)"


class Customer(models.Model):
    """ग्राहक प्रबंधन - Customer Management"""
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    purchase_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Customers (ग्राहक)"


class Credit(models.Model):
    """क्रेडिट/ऋण प्रबंधन - Credit/Loan System"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
        ('Written_Off', 'Written Off'),
    ]

    customer = models.ForeignKey(Customer, related_name='credits', on_delete=models.CASCADE)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    date_issued = models.DateField()
    due_date = models.DateField()
    paid_amount = models.FloatField(validators=[MinValueValidator(0)], default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def remaining_amount(self):
        return max(0, self.amount - self.paid_amount)

    def save(self, *args, **kwargs):
        # FIX: paid_amount ke basis par status auto-update karo (Written_Off manual rahega)
        if self.status != 'Written_Off':
            today = date.today()
            if self.paid_amount >= self.amount:
                self.status = 'Paid'
            elif self.paid_amount > 0:
                self.status = 'Partial'
            elif self.due_date < today:
                self.status = 'Overdue'
            else:
                self.status = 'Pending'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} — ₹{self.amount} ({self.status})"

    class Meta:
        verbose_name_plural = "Credits (क्रेडिट/ऋण)"


class Notification(models.Model):
    """सूचनाएं - Notifications"""
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        read_status = "✓" if self.is_read else "●"
        return f"{read_status} {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Notifications (सूचनाएं)"


class Insurance(models.Model):
    """बीमा प्रबंधन - Insurance Management"""
    goat = models.ForeignKey(Goat, related_name='insurance', on_delete=models.CASCADE)
    provider = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=100)
    coverage_amount = models.FloatField(validators=[MinValueValidator(0)])
    premium = models.FloatField(validators=[MinValueValidator(0)])
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goat.name} — {self.provider} ({self.policy_number})"

    class Meta:
        verbose_name_plural = "Insurance (बीमा)"


class MortalityRecord(models.Model):
    """मृत्यु रिकॉर्ड - Mortality Records"""
    goat = models.ForeignKey(Goat, related_name='mortality', on_delete=models.CASCADE)
    death_date = models.DateField()
    cause = models.TextField()
    age_at_death = models.IntegerField(validators=[MinValueValidator(0)])
    weight_at_death = models.FloatField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update goat status to 'D' (Dead)
        Goat.objects.filter(pk=self.goat_id).update(status='D')

    def __str__(self):
        return f"{self.goat.name} — died {self.death_date} ({self.cause[:50]})"

    class Meta:
        verbose_name_plural = "Mortality Records (मृत्यु रिकॉर्ड)"


class AdditionalIncome(models.Model):
    """अतिरिक्त आय - Additional Income"""
    source = models.CharField(max_length=200)
    amount = models.FloatField(validators=[MinValueValidator(0)])
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} — ₹{self.amount} ({self.date})"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Additional Income (अतिरिक्त आय)"


class ActivityLog(models.Model):
    """गतिविधि लॉग - Activity Logs"""
    action = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.action} — {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Activity Logs (गतिविधि लॉग)"


class VetVisit(models.Model):
    """पशुचिकित्सक दौरा - Vet Visits"""
    date = models.DateField()
    vet_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    goats_visited = models.ManyToManyField(Goat)
    observations = models.TextField()
    recommendations = models.TextField(blank=True)
    cost = models.FloatField(validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.vet_name} — {self.date}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Vet Visits (पशुचिकित्सक दौरा)"


class VaccinationSchedule(models.Model):
    """टीकाकरण समय सारणी - Vaccination Schedule"""
    goat = models.ForeignKey(Goat, related_name='vaccination_schedule', on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # FIX: completed=True karne par completion_date auto-set karo agar blank hai
        if self.completed and not self.completion_date:
            self.completion_date = date.today()
        # FIX: completed=False karne par completion_date clear karo
        elif not self.completed:
            self.completion_date = None
        super().save(*args, **kwargs)

    def __str__(self):
        done = "✓" if self.completed else "○"
        return f"{done} {self.goat.name} — {self.vaccine_name} (due: {self.due_date})"

    class Meta:
        ordering = ['due_date']
        verbose_name_plural = "Vaccination Schedule (टीकाकरण समय सारणी)"


class BudgetPlanning(models.Model):
    """बजट योजना - Budget Planning"""
    category = models.CharField(max_length=100)
    planned_amount = models.FloatField(validators=[MinValueValidator(0)])
    actual_amount = models.FloatField(validators=[MinValueValidator(0)], default=0)
    month = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} — {self.month.strftime('%b %Y')} (₹{self.planned_amount})"

    class Meta:
        ordering = ['-month']
        verbose_name_plural = "Budget Planning (बजट योजना)"


class PerformanceEvaluation(models.Model):
    """प्रदर्शन मूल्यांकन - Performance Evaluation"""
    CATEGORY_CHOICES = [
        ('E', 'Excellent'),
        ('G', 'Good'),
        ('A', 'Average'),
        ('BA', 'Below Average'),
        ('P', 'Poor'),
    ]
    
    goat = models.ForeignKey(Goat, related_name='performance_evaluations', on_delete=models.CASCADE)
    weight_score = models.IntegerField(validators=[MinValueValidator(0)])
    milk_production_score = models.IntegerField(validators=[MinValueValidator(0)])
    health_score = models.IntegerField(validators=[MinValueValidator(0)])
    breeding_score = models.IntegerField(validators=[MinValueValidator(0)])
    overall_category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    total_score = models.IntegerField(validators=[MinValueValidator(0)])
    percentage = models.FloatField(validators=[MinValueValidator(0)])
    evaluation_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goat.name} — {self.evaluation_date} ({self.get_overall_category_display()}, {self.percentage:.1f}%)"

    class Meta:
        ordering = ['-evaluation_date']
        verbose_name_plural = "Performance Evaluation (प्रदर्शन मूल्यांकन)"


class CustomReminder(models.Model):
    """कस्टम रिमाइंडर - Custom Reminders"""
    REMINDER_TYPE_CHOICES = [
        ('OT', 'One-Time'),
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
        ('Y', 'Yearly'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    reminder_type = models.CharField(max_length=2, choices=REMINDER_TYPE_CHOICES)
    scheduled_time = models.TimeField()
    goat = models.ForeignKey(Goat, null=True, blank=True, related_name='reminders', on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        active = "Active" if self.is_active else "Inactive"
        return f"{self.title} ({self.get_reminder_type_display()}) — {active}"

    class Meta:
        verbose_name_plural = "Custom Reminders (कस्टम रिमाइंडर)"


class Document(models.Model):
    """दस्तावेज़ प्रबंधन - Document Management"""
    DOCUMENT_TYPE_CHOICES = [
        ('CERT', 'Certificate'),
        ('LIC', 'License'),
        ('INS', 'Insurance'),
        ('MED', 'Medical'),
        ('PURCH', 'Purchase'),
        ('SALE', 'Sale'),
        ('LEGAL', 'Legal'),
    ]
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES)
    file_path = models.CharField(max_length=500, null=True, blank=True)  # Document file path or URL
    document_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    goat = models.ForeignKey(Goat, null=True, blank=True, related_name='documents', on_delete=models.SET_NULL)
    tags = models.CharField(max_length=200, blank=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} — {self.title}"

    class Meta:
        verbose_name_plural = "Documents (दस्तावेज़)"


class PhotoGallery(models.Model):
    """फोटो गैलरी - Photo Gallery"""
    CATEGORY_CHOICES = [
        ('GOAT', 'Goat Photos'),
        ('FARM', 'Farm Photos'),
        ('EVENT', 'Event'),
        ('PROD', 'Product'),
        ('ACHIEVE', 'Achievement'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    photo_url = models.CharField(max_length=500)  # Photo URL or path
    date_taken = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    photographer = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    goat = models.ForeignKey(Goat, null=True, blank=True, related_name='gallery_photos', on_delete=models.SET_NULL)
    featured = models.BooleanField(default=False)
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()}) — {self.date_taken}"

    class Meta:
        ordering = ['-date_taken']
        verbose_name_plural = "Photo Gallery (फोटो गैलरी)"


class WeatherRecord(models.Model):
    """मौसम रिकॉर्ड - Weather Records"""
    date = models.DateField()
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    avg_temperature = models.FloatField()
    humidity = models.FloatField()
    rainfall = models.FloatField(validators=[MinValueValidator(0)], default=0)
    weather_condition = models.CharField(max_length=100)
    impact_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} — {self.weather_condition} ({self.min_temperature}°C – {self.max_temperature}°C)"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Weather Records (मौसम रिकॉर्ड)"


class MarketPrice(models.Model):
    """बाजार मूल्य - Market Prices"""
    ITEM_CHOICES = [
        ('LIVE_GOAT', 'Live Goat'),
        ('MEAT', 'Meat'),
        ('MILK', 'Milk'),
        ('MANURE', 'Manure'),
        ('HAIR', 'Hair/Wool'),
        ('SKIN', 'Skin'),
        ('FEED', 'Feed'),
        ('MEDICINE', 'Medicine'),
    ]
    QUALITY_CHOICES = [
        ('PREMIUM', 'Premium'),
        ('STANDARD', 'Standard'),
        ('ECONOMY', 'Economy'),
    ]
    
    item = models.CharField(max_length=20, choices=ITEM_CHOICES)
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES)
    market = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    price = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20)
    date_recorded = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_item_display()} — ₹{self.price}/{self.unit} at {self.market} ({self.date_recorded})"

    class Meta:
        ordering = ['-date_recorded']
        verbose_name_plural = "Market Prices (बाजार मूल्य)"


class FarmEvent(models.Model):
    """फार्म इवेंट - Farm Events & Milestones"""
    EVENT_TYPE_CHOICES = [
        ('BIRTH', 'Birth'),
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('VACCINATION', 'Vaccination'),
        ('MEDICAL', 'Medical Event'),
        ('ACHIEVEMENT', 'Achievement'),
        ('EXPANSION', 'Expansion'),
        ('TRAINING', 'Training'),
        ('VISIT', 'Visitor'),
    ]
    
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    date = models.DateField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    goats_involved = models.ManyToManyField(Goat, blank=True)
    attendees = models.CharField(max_length=500, blank=True)
    cost = models.FloatField(validators=[MinValueValidator(0)], default=0)
    photo_url = models.CharField(max_length=500, blank=True)  # Photo URL or path
    is_milestone = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        milestone = " ⭐" if self.is_milestone else ""
        return f"{self.get_event_type_display()} — {self.title} ({self.date}){milestone}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Farm Events (फार्म इवेंट)"


class BreedingPlan(models.Model):
    """प्रजनन योजना - Breeding Plans & Strategy"""
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_breedings = models.IntegerField(validators=[MinValueValidator(0)])
    target_births = models.IntegerField(validators=[MinValueValidator(0)])
    target_breeds = models.CharField(max_length=200)
    budget = models.FloatField(validators=[MinValueValidator(0)])
    actual_spent = models.FloatField(validators=[MinValueValidator(0)], default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    actual_breedings = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    actual_births = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    success_rate = models.FloatField(validators=[MinValueValidator(0)], default=0)
    achievement_percentage = models.FloatField(validators=[MinValueValidator(0)], default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    strategy_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()}) — {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Breeding Plans (प्रजनन योजना)"
