<script setup>
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useConsultationStore } from '@/stores/consultation';

const route = useRoute();
const store = useConsultationStore();

onMounted(() => store.loadSummary(route.params.id));

</script>

<template>

    <div class="max-w-2xl mx-auto p-6 flex flex-col gap-6">
        <h1 class="text-2xl font-bold">Your Consultation Summary</h1>

        <div v-if="store.loading" class="flex flex-col gap-4">
            <Skeleton class="h-32 w-full" />
            <Skeleton class="h-24 w-full" />
        </div>

        <template v-else-if="store.consultation">
            <Card>
                <CardHeader>
                    <CardTitle>Diagnosis</CardTitle>
                </CardHeader>
                <CardContent>
                    <p>{{ store.consultation.diagnosis }}</p>
                </CardContent>
            </Card>

            <Card v-if="store.consultation.prescription_items?.length">
                <CardHeader>
                    <CardTitle>Prescribed Medications</CardTitle>
                </CardHeader>
                <CardContent>
                    <ul class="flex flex-col gap-2">
                        <li v-for="(item, i) in store.consultation.prescription_items" :key="i"
                            class="flex items-center gap-2">
                            <Badge variant="secondary">{{ item.name }}</Badge>
                            <span class="text-sm text-muted-foreground">
                                {{ item.dose }} — {{ item.frequency }}
                            </span>
                        </li>
                    </ul>
                </CardContent>
            </Card>

            <Card v-if="store.consultation.requested_tests?.length">
                <CardHeader>
                    <CardTitle>Requested Tests</CardTitle>
                </CardHeader>
                <CardContent>
                    <ul class="flex flex-col gap-2">
                        <li v-for="(test, i) in store.consultation.requested_tests" :key="i"
                            class="flex items-center gap-2">
                            <Badge variant="outline">{{ test.name }}</Badge>
                            <span v-if="test.notes" class="text-sm text-muted-foreground">
                                {{ test.notes }}
                            </span>
                        </li>
                    </ul>
                </CardContent>
            </Card>

            <p v-else class="text-muted-foreground">No consultation record found.</p>
            <p v-if="store.error" class="text-destructive text-sm">{{ store.error }}</p>

        </template>
    </div>
</template>