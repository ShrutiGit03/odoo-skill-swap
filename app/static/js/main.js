document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle swap request button clicks
    document.querySelectorAll('.request-swap-btn').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            const skillId = this.getAttribute('data-skill-id');
            const skillType = this.getAttribute('data-skill-type');
            
            document.getElementById('receiverId').value = userId;
            document.getElementById('targetSkillId').value = skillId;
            document.getElementById('targetSkillType').value = skillType;
            
            // Reset form
            document.getElementById('offeredSkill').value = '';
            document.getElementById('wantedSkill').innerHTML = '<option value="">Select a skill...</option>';
            document.getElementById('swapMessage').value = '';
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('swapModal'));
            modal.show();
        });
    });
    
    // When user selects a skill to offer, populate wanted skills
    document.getElementById('offeredSkill')?.addEventListener('change', function() {
        const receiverId = document.getElementById('receiverId').value;
        const targetSkillType = document.getElementById('targetSkillType').value;
        
        if (this.value && receiverId) {
            fetch(`/api/user_skills/${receiverId}/${targetSkillType}`)
                .then(response => response.json())
                .then(data => {
                    const select = document.getElementById('wantedSkill');
                    select.innerHTML = '<option value="">Select a skill...</option>';
                    data.skills.forEach(skill => {
                        const option = document.createElement('option');
                        option.value = skill.id;
                        option.textContent = skill.name;
                        select.appendChild(option);
                    });
                })
                .catch(error => console.error('Error:', error));
        }
    });
    
    // Submit swap request
    document.getElementById('submitSwapRequest')?.addEventListener('click', function() {
        const receiverId = document.getElementById('receiverId').value;
        const offeredSkillId = document.getElementById('offeredSkill').value;
        const wantedSkillId = document.getElementById('wantedSkill').value;
        const message = document.getElementById('swapMessage').value;
        
        if (!offeredSkillId || !wantedSkillId) {
            alert('Please select both skills for the swap');
            return;
        }
        
        fetch('/request_swap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                receiver_id: receiverId,
                offered_skill_id: offeredSkillId,
                wanted_skill_id: wantedSkillId,
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Swap request sent successfully!');
                bootstrap.Modal.getInstance(document.getElementById('swapModal')).hide();
                // Optionally refresh the page or update UI
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while sending the request');
        });
    });

    // Handle profile picture upload preview
    const profilePicInput = document.getElementById('profilePic');
    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('profilePicPreview').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Mark notifications as read when clicked
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.getAttribute('data-notification-id');
            if (notificationId) {
                fetch(`/mark_notification_read/${notificationId}`, { method: 'POST' });
            }
        });
    });
});