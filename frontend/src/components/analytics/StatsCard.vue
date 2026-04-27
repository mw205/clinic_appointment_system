<script setup>
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Ticket } from 'lucide-vue-next';
import Card from '../card/Card.vue';
import CardHeader from '../card/CardHeader.vue';
import CardTitle from '../card/CardTitle.vue';
import CardDescription from '../card/CardDescription.vue';
import CardContent from '../card/CardContent.vue';
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