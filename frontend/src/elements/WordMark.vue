<template>
  <div class="wrapper">
    <div class="logo"></div>
    <h1 class="title" aria-label="Thunderbird Pro Appointment.">
      <span>Thunderbird Pro</span> Appointment
    </h1>
  </div>
</template>

<style scoped>
.title {
  display: flex;
  flex-direction: column;

  color: var(--ti-base);
  font-family: 'Metropolis', sans-serif;
  font-weight: 200;
  font-size: 2rem;
  line-height: 2rem;

  span {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.938rem;
    line-height: 1.134rem;
  }
}

.wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo {
  background-image: url('@/assets/svg/logo.svg');
  background-size: contain;
  background-repeat: no-repeat;
  width: 4rem;
  height: 4rem;
}
</style>
