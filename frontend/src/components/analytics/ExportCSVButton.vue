<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { useAnalyticsStore } from '@/stores/analytics'

const props = defineProps({
    type: String,
    label: String
})

const analyticsStore = useAnalyticsStore()
const exporting = ref(false)
async function handleExport() {
    exporting.value = true
    await analyticsStore.exportCSV(props.type)
    exporting.value = false
}
</script>

<template>
    <Button variant="outline" :disabled="exporting" @click="handleExport">
        {{ exporting ? 'Downloading...' : label }}
    </Button>
</template>