<template>
  <div class="space-y-6">
    <div>
      <h3 class="text-lg font-medium">Profile</h3>
      <p class="text-sm text-gray-500">
        Update your role-specific profile information.
      </p>
    </div>
    
    <div class="border-t pt-6"></div>

    <div v-if="isLoadingData" class="text-gray-500">
      Loading profile...
    </div>

    <!-- PATIENT PROFILE -->
    <form v-else-if="user?.primary_role === 'Patient'" @submit.prevent="handleUpdatePatient" class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="date_of_birth">Date of Birth</Label>
          <Input id="date_of_birth" type="date" v-model="patientForm.date_of_birth" :disabled="isSaving" />
        </div>
        <div class="space-y-2">
          <Label for="blood_type">Blood Type</Label>
          <select id="blood_type" v-model="patientForm.blood_type" :disabled="isSaving" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
            <option value="" disabled>Select</option>
            <option value="A+">A+</option>
            <option value="A-">A-</option>
            <option value="B+">B+</option>
            <option value="B-">B-</option>
            <option value="AB+">AB+</option>
            <option value="AB-">AB-</option>
            <option value="O+">O+</option>
            <option value="O-">O-</option>
          </select>
        </div>
      </div>

      <div class="space-y-2">
        <Label for="gender">Gender</Label>
        <select id="gender" v-model="patientForm.gender" :disabled="isSaving" class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
          <option value="" disabled>Select</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </div>

      <Button type="submit" class="bg-teal-600 hover:bg-teal-700" :disabled="isSaving">
        {{ isSaving ? 'Saving...' : 'Update Profile' }}
      </Button>
      
      <p v-if="successMessage" class="text-green-600 text-sm mt-2">{{ successMessage }}</p>
      <div v-if="errorMessage" class="text-red-500 text-sm mt-2 whitespace-pre-wrap">{{ errorMessage }}</div>
    </form>

    <!-- DOCTOR PROFILE -->
    <form v-else-if="user?.primary_role === 'Doctor'" @submit.prevent="handleUpdateDoctor" class="space-y-4 max-w-md">
      <div class="space-y-2">
        <Label for="specialization">Specialization</Label>
        <Input id="specialization" v-model="doctorForm.specialization" required :disabled="isSaving" />
      </div>

      <Button type="submit" class="bg-teal-600 hover:bg-teal-700" :disabled="isSaving">
        {{ isSaving ? 'Saving...' : 'Update Profile' }}
      </Button>

      <p v-if="successMessage" class="text-green-600 text-sm mt-2">{{ successMessage }}</p>
      <div v-if="errorMessage" class="text-red-500 text-sm mt-2 whitespace-pre-wrap">{{ errorMessage }}</div>
    </form>

    <div v-else class="text-gray-500 italic">
      No specific profile settings are available for your role.
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { useAuth } from "@/composables/useAuth";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const { user, getPatientProfile, updatePatientProfile, getDoctorProfile, updateDoctorProfile } = useAuth();

const isLoadingData = ref(false);
const isSaving = ref(false);
const successMessage = ref("");
const errorMessage = ref("");

const patientForm = reactive({
  date_of_birth: "",
  blood_type: "",
  gender: "",
});

const doctorForm = reactive({
  specialization: "",
});

const loadProfile = async () => {
  if (!user.value) return;

  errorMessage.value = "";
  successMessage.value = "";

  if (user.value.primary_role === 'Patient') {
    isLoadingData.value = true;
    try {
      const data = await getPatientProfile();
      patientForm.date_of_birth = data.date_of_birth || "";
      patientForm.blood_type = data.blood_type || "";
      patientForm.gender = data.gender || "";
    } catch (e) {
      console.error("Failed to load patient profile", e);
    } finally {
      isLoadingData.value = false;
    }
  } else if (user.value.primary_role === 'Doctor') {
    isLoadingData.value = true;
    try {
      const data = await getDoctorProfile();
      doctorForm.specialization = data.specialization || "";
    } catch (e) {
      console.error("Failed to load doctor profile", e);
    } finally {
      isLoadingData.value = false;
    }
  }
};

onMounted(() => {
  loadProfile();
});

watch(user, () => {
  loadProfile();
}, { deep: true });

const handleUpdatePatient = async () => {
  isSaving.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  
  try {
    await updatePatientProfile(patientForm);
    successMessage.value = "Patient profile updated successfully.";
  } catch (error) {
    handleError(error);
  } finally {
    isSaving.value = false;
  }
};

const handleUpdateDoctor = async () => {
  isSaving.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  
  try {
    await updateDoctorProfile(doctorForm);
    successMessage.value = "Doctor profile updated successfully.";
  } catch (error) {
    handleError(error);
  } finally {
    isSaving.value = false;
  }
};

const handleError = (error) => {
  const data = error.response?.data;
  const dataErrors = data?.errors || data?.details || data;

  if (dataErrors && typeof dataErrors === 'object') {
      const errors = [];
      for (const [key, val] of Object.entries(dataErrors)) {
          let msg = Array.isArray(val) ? val.join(', ') : val;
          const noPrefixKeys = ['non_field_errors', 'detail'];
          const prefix = noPrefixKeys.includes(key) ? '' : `${key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}: `;
          errors.push(`${prefix}${msg}`);
      }
      errorMessage.value = errors.join('\n');
  } else {
      errorMessage.value = "Failed to update profile.";
  }
};
</script>
