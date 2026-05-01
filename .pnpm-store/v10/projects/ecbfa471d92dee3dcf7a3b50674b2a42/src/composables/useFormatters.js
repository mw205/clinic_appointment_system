export const useFormatters = () => {

   const formatTime = (timestamp) =>
    new Date(timestamp).toLocaleTimeString('en-GB', {
      timeZone: 'UTC',
    })

  const formatDate = (timestamp) =>
    new Date(timestamp).toLocaleDateString('en-GB', {
      timeZone: 'UTC'
    })


  function formatDateTime(timestamp) {
    return new Date(timestamp).toLocaleString('en-GB', {
      timeZone: 'UTC'
    })
  }

  return {
    formatTime,
    formatDate,
    formatDateTime
  }
}
