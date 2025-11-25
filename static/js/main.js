// وظائف عامة للتطبيق

// عرض رسالة تنبيه
function showAlert(message, type = 'info') {
    // ترجمة الرسالة إذا كانت key
    if (window.translator && message.startsWith('messages.')) {
        message = translator.translate(message);
    }
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    
    const icon = {
        'success': 'fa-check-circle',
        'danger': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    }[type] || 'fa-info-circle';
    
    alertDiv.innerHTML = `
        <i class="fa ${icon}"></i>
        <span>${message}</span>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// إرسال طلب AJAX
async function sendRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('خطأ في الطلب:', error);
        showAlert('messages.error_connection', 'danger');
        return null;
    }
}

// البحث عن المرضى
let searchTimeout;
function searchPatients(query) {
    clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(async () => {
        if (query.length < 2) return;
        
        const result = await sendRequest(`/api/search-patients?q=${encodeURIComponent(query)}`);
        
        if (result && result.results) {
            displaySearchResults(result.results, 'patients');
        }
    }, 300);
}

// البحث عن الأدوية
function searchDrugs(query) {
    clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(async () => {
        if (query.length < 2) return;
        
        const result = await sendRequest(`/api/search-drugs?q=${encodeURIComponent(query)}`);
        
        if (result && result.results) {
            displaySearchResults(result.results, 'drugs');
        }
    }, 300);
}

// عرض نتائج البحث
function displaySearchResults(results, type) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        const noResults = translator ? translator.translate('messages.no_results') : 'لا توجد نتائج';
        resultsContainer.innerHTML = `<div class="list-item">${noResults}</div>`;
        return;
    }
    
    results.forEach(item => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'list-item';
        resultDiv.style.cursor = 'pointer';
        
        if (type === 'patients') {
            resultDiv.innerHTML = `
                <strong>${item.name}</strong>
                <span style="color: var(--text-muted); margin-right: 10px;">رقم الملف: ${item.file_number}</span>
            `;
            resultDiv.onclick = () => {
                window.location.href = `/patient/${item.id}`;
            };
        } else if (type === 'drugs') {
            resultDiv.innerHTML = `
                <strong>${item.name}</strong>
                <span class="badge badge-info" style="margin-right: 10px;">${item.category}</span>
            `;
            resultDiv.onclick = () => {
                window.location.href = `/drug/${item.id}`;
            };
        }
        
        resultsContainer.appendChild(resultDiv);
    });
}

// إدارة الحقول الديناميكية
function addDynamicField(containerId, fieldName, placeholder = '') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'dynamic-field';
    
    fieldDiv.innerHTML = `
        <input type="text" name="${fieldName}[]" class="form-control" placeholder="${placeholder}">
        <button type="button" class="btn-remove" onclick="removeDynamicField(this)">
            <i class="fa fa-times"></i>
        </button>
    `;
    
    container.appendChild(fieldDiv);
}

function removeDynamicField(button) {
    button.parentElement.remove();
}

// حفظ بيانات المريض
async function savePatient(formId, patientId = null) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    
    const url = patientId ? `/patient/${patientId}/edit` : '/patient/new';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('messages.patient_saved', 'success');
            setTimeout(() => {
                window.location.href = `/patient/${result.patient_id}`;
            }, 1000);
        } else {
            const errors = result.errors.join('<br>');
            showAlert(errors, 'danger');
        }
    } catch (error) {
        console.error('خطأ:', error);
        showAlert('messages.error_saving', 'danger');
    }
}

// حفظ بيانات الدواء
async function saveDrug(formId, drugId = null) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    
    const url = drugId ? `/drug/${drugId}/edit` : '/drug/new';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('messages.drug_saved', 'success');
            setTimeout(() => {
                window.location.href = `/drug/${result.drug_id}`;
            }, 1000);
        } else {
            const errors = result.errors.join('<br>');
            showAlert(errors, 'danger');
        }
    } catch (error) {
        console.error('خطأ:', error);
        showAlert('messages.error_saving', 'danger');
    }
}

// اقتراح وصفة طبية
async function suggestPrescription(patientId) {
    const symptoms = document.getElementById('symptoms')?.value || '';
    const diagnosis = document.getElementById('diagnosis')?.value || '';
    
    if (!symptoms && !diagnosis) {
        showAlert('messages.enter_symptoms', 'warning');
        return;
    }
    
    const loadingDiv = document.getElementById('loading');
    const suggestionsDiv = document.getElementById('suggestions');
    
    if (loadingDiv) loadingDiv.classList.remove('hidden');
    if (suggestionsDiv) suggestionsDiv.innerHTML = '';
    
    const result = await sendRequest('/api/suggest-prescription', 'POST', {
        patient_id: patientId,
        symptoms: symptoms,
        diagnosis: diagnosis
    });
    
    if (loadingDiv) loadingDiv.classList.add('hidden');
    
    if (result && result.success) {
        displaySuggestions(result.suggestions);
    }
}

// عرض الاقتراحات
function displaySuggestions(suggestions) {
    const suggestionsDiv = document.getElementById('suggestions');
    if (!suggestionsDiv) return;
    
    suggestionsDiv.innerHTML = '';
    
    if (suggestions.length === 0) {
        const noSuggestions = translator ? translator.translate('messages.no_suggestions') : 'لا توجد اقتراحات متاحة';
        suggestionsDiv.innerHTML = `<div class="alert alert-info">${noSuggestions}</div>`;
        return;
    }
    
    suggestions.forEach((suggestion, index) => {
        const card = document.createElement('div');
        card.className = 'suggestion-card';
        card.dataset.index = index;
        
        const safety = suggestion.safety;
        
        if (safety.severity === 'high') {
            card.classList.add('has-danger');
        } else if (safety.severity === 'medium' || safety.severity === 'low') {
            card.classList.add('has-warning');
        }
        
        let warningsHtml = '';
        if (safety.warnings.length > 0) {
            warningsHtml = '<div class="mt-2">';
            safety.warnings.forEach(warning => {
                const alertType = safety.severity === 'high' ? 'danger' : 'warning';
                warningsHtml += `<div class="alert alert-${alertType}" style="margin-bottom: 8px; padding: 10px;">${warning}</div>`;
            });
            warningsHtml += '</div>';
        }
        
        card.innerHTML = `
            <div class="drug-name">${suggestion.drug.name}</div>
            <div class="drug-details">
                <div class="drug-detail">
                    <span class="drug-detail-label">الفئة:</span>
                    <span class="drug-detail-value">${suggestion.drug.category}</span>
                </div>
                <div class="drug-detail">
                    <span class="drug-detail-label">الجرعة المقترحة:</span>
                    <span class="drug-detail-value">${suggestion.recommended_dosage}</span>
                </div>
                <div class="drug-detail">
                    <span class="drug-detail-label">الوصف:</span>
                    <span class="drug-detail-value">${suggestion.drug.description || 'غير متوفر'}</span>
                </div>
            </div>
            ${warningsHtml}
            <div class="mt-2">
                <button type="button" class="btn btn-primary btn-sm" onclick="selectDrug(${index}, ${safety.safe})">
                    <i class="fa fa-plus"></i> إضافة للوصفة
                </button>
            </div>
        `;
        
        suggestionsDiv.appendChild(card);
    });
}

// اختيار دواء
let selectedDrugs = [];

function selectDrug(index, isSafe) {
    const card = document.querySelector(`.suggestion-card[data-index="${index}"]`);
    if (!card) return;
    
    if (!isSafe) {
        const warningMsg = translator ? translator.translate('messages.unsafe_drug_warning') : 'تحذير: هذا الدواء قد يكون غير آمن للمريض. هل تريد المتابعة؟';
        const confirmed = confirm(warningMsg);
        if (!confirmed) return;
    }
    
    const drugName = card.querySelector('.drug-name').textContent;
    const dosage = card.querySelector('.drug-detail-value').textContent;
    
    const drug = {
        drug_name: drugName,
        dosage: dosage,
        duration: '',
        instructions: 'حسب إرشادات الطبيب'
    };
    
    selectedDrugs.push(drug);
    card.classList.add('selected');
    
    updateSelectedDrugsList();
    showAlert('messages.drug_added', 'success');
}

// تحديث قائمة الأدوية المختارة
function updateSelectedDrugsList() {
    const listDiv = document.getElementById('selected-drugs-list');
    if (!listDiv) return;
    
    listDiv.innerHTML = '';
    
    if (selectedDrugs.length === 0) {
        const noDrugs = translator ? translator.translate('prescription.no_drugs_selected') : 'لم يتم اختيار أي أدوية بعد';
        listDiv.innerHTML = `<div class="alert alert-info">${noDrugs}</div>`;
        return;
    }
    
    selectedDrugs.forEach((drug, index) => {
        const drugDiv = document.createElement('div');
        drugDiv.className = 'prescription-item';
        
        drugDiv.innerHTML = `
            <div class="drug-name">${drug.drug_name}</div>
            <div class="drug-details">
                <div class="form-group">
                    <label class="form-label">الجرعة:</label>
                    <input type="text" class="form-control" value="${drug.dosage}" 
                           onchange="updateDrugField(${index}, 'dosage', this.value)">
                </div>
                <div class="form-group">
                    <label class="form-label">المدة:</label>
                    <input type="text" class="form-control" value="${drug.duration}" 
                           placeholder="مثال: 7 أيام"
                           onchange="updateDrugField(${index}, 'duration', this.value)">
                </div>
                <div class="form-group">
                    <label class="form-label">التعليمات:</label>
                    <textarea class="form-control" 
                              onchange="updateDrugField(${index}, 'instructions', this.value)">${drug.instructions}</textarea>
                </div>
            </div>
            <button type="button" class="btn btn-danger btn-sm mt-2" onclick="removeDrug(${index})">
                <i class="fa fa-trash"></i> إزالة
            </button>
        `;
        
        listDiv.appendChild(drugDiv);
    });
}

// تحديث حقل دواء
function updateDrugField(index, field, value) {
    if (selectedDrugs[index]) {
        selectedDrugs[index][field] = value;
    }
}

// إزالة دواء
function removeDrug(index) {
    selectedDrugs.splice(index, 1);
    updateSelectedDrugsList();
    showAlert('messages.drug_removed', 'info');
}

// حفظ الوصفة
async function savePrescription(patientId) {
    if (selectedDrugs.length === 0) {
        showAlert('messages.select_drugs', 'warning');
        return;
    }
    
    const symptoms = document.getElementById('symptoms')?.value || '';
    const diagnosis = document.getElementById('diagnosis')?.value || '';
    const doctorName = document.getElementById('doctor_name')?.value || 'د. غير محدد';
    const notes = document.getElementById('notes')?.value || '';
    
    const data = {
        symptoms: symptoms,
        diagnosis: diagnosis,
        doctor_name: doctorName,
        notes: notes,
        prescription: selectedDrugs
    };
    
    const result = await sendRequest(`/patient/${patientId}/prescribe`, 'POST', data);
    
    if (result && result.success) {
        showAlert('messages.prescription_saved', 'success');
        setTimeout(() => {
            window.location.href = `/patient/${patientId}`;
        }, 1000);
    }
}

// فحص التداخل الدوائي
async function checkInteraction(drugId, patientId) {
    const result = await sendRequest('/api/check-interaction', 'POST', {
        drug_id: drugId,
        patient_id: patientId
    });
    
    if (result && result.success) {
        const safety = result.safety;
        
        if (safety.warnings.length > 0) {
            let message = 'تحذيرات:<br>' + safety.warnings.join('<br>');
            showAlert(message, safety.severity === 'high' ? 'danger' : 'warning');
        } else {
            showAlert('messages.no_interactions', 'success');
        }
    }
}

// Modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// إغلاق Modal عند الضغط خارجها
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// تهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    // إضافة مستمع للبحث
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        const searchType = searchInput.dataset.type;
        searchInput.addEventListener('input', (e) => {
            if (searchType === 'patients') {
                searchPatients(e.target.value);
            } else if (searchType === 'drugs') {
                searchDrugs(e.target.value);
            }
        });
    }
});
