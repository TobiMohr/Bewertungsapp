<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">Data Import & Export</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Export Section -->
      <div class="p-6 bg-white rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-4">Export Data</h2>
        <p class="text-gray-600 mb-4">
          Click below to export all users and evaluations as a XLSX file.
        </p>
        <BaseButton @click="handleExport" :loading="isExporting">
          {{ isExporting ? "Exporting..." : "Export XLSX" }}
        </BaseButton>
      </div>

      <!-- Import Section -->
      <div class="p-6 bg-white rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-4">Import Data</h2>
        <p class="text-gray-600 mb-4">
          Choose a XLSX file containing users and click “Import”.
        </p>

        <input
          type="file"
          accept=".xlsx"
          @change="handleFileChange"
          class="mb-4"
        />

        <BaseButton
          :disabled="!selectedFile"
          @click="handleImport"
          :loading="isImporting"
        >
          {{ isImporting ? "Importing..." : "Import XLSX" }}
        </BaseButton>

        <p v-if="message" class="mt-4 text-sm" :class="messageClass">
          {{ message }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import BaseButton from "../BaseComponents/BaseButton.vue";
import { exportUsersXLSX, importUsersXLSX } from "@/api/files";

const selectedFile = ref(null);
const isExporting = ref(false);
const isImporting = ref(false);
const message = ref("");

// Message color
const messageClass = computed(() =>
  message.value.includes("success") ? "text-green-600" : "text-red-600"
);

// Handle file input
const handleFileChange = (e) => {
  selectedFile.value = e.target.files[0];
  message.value = "";
};

// Export
const handleExport = async () => {
  isExporting.value = true;
  try {
    const response = await exportUsersXLSX();
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "users.xlsx");
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    message.value = "Error exporting users.";
  } finally {
    isExporting.value = false;
  }
};

// Import
const handleImport = async () => {
  if (!selectedFile.value) return;
  isImporting.value = true;
  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    await importUsersXLSX(formData);
    message.value = "Users imported successfully!";
  } catch (err) {
    console.error(err);
    message.value = "Error importing users.";
  } finally {
    isImporting.value = false;
  }
};
</script>

<style scoped>
input[type="file"] {
  display: block;
}
</style>
