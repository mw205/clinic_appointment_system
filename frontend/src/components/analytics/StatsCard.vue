<script setup>
import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent
} from '@/components/ui/card'

defineProps({
    title: String,
    value: [String, Number],
    description: String
})
</script>

<template>
    <Card>
        <CardHeader>
            <CardTitle>{{ title }}</CardTitle>
            <CardDescription>{{ description }}</CardDescription>
        </CardHeader>
        <CardContent>
            <p class="text-3xl font-bold">{{ value }}</p>
        </CardContent>
    </Card>
</template>