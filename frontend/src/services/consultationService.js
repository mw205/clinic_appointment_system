//the url of back end server

export const BASE_URL = 'https://localhost:8000/api'

export function getAuthenticantionHeaders() {
    const token = localStorage.getItem('token')
    return {
        'type': 'application/json',
        'method': `Bearer ${token}`
    }
}

export async function fetchConsultation(appointmentId) {

    const response = await fetch(`${BASE_URL}/consultations/?appointment=${appointmentId}`,
        { headers: getAuthenticantionHeaders() }
    )
    if (!response.ok)
        return null;
    return response.json();


}

export async function createConsultation(data) {
    const response = await fetch(`${BASE_URL}/consultations/`,
        {
            method: 'POST',
            headers: getAuthenticantionHeaders(),
            body: JSON.stringify(data)
        })
    if (!response.ok) throw new Error('error at creating consultaion')
    return response.json()
}
export async function updateConsultation(id, data) {
    const response = await fetch(`${BASE_URL}/consultations/${id}/`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('error at updating consultation')
    return response.json()
}

export async function fetchConsultationSummary(id) {
    const response = await fetch(`${BASE_URL}/consultations/${id}/summary/`,
        { headers: getAuthenticantionHeaders() }
    )
    if (!response.ok)
        return null;
    return response.json();

}