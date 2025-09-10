<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import InfoBox from '@/elements/home/InfoBox.vue';
import ArtLogo from '@/elements/arts/ArtLogo.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { useUserStore } from '@/stores/user-store';
import { ColourSchemes } from '@/definitions';

const router = useRouter();

const userStore = useUserStore();
const { authenticated: isAuthenticated } = storeToRefs(userStore);

const isDarkMode = computed(() => userStore.myColourScheme === ColourSchemes.Dark);

const enter = () => {
  router.push({ name: 'dashboard' });
};
const login = () => {
  router.push({ name: 'login' });
};
const signUp = () => {
  router.push({ name: 'join-the-waiting-list' });
};
</script>

<template>
  <div>
    <section class="first-section-container">
      <ArtLogo class="art-logo"/>
      <div class="content">
        <h4>
          {{ $t('text.homepage.intro') }}
        </h4>
        <div class="button-container">
          <template v-if="!isAuthenticated">
            <primary-button
              :label="$t('label.logIn')"
              @click="login"
              :title="$t('label.logIn')"
              data-testid="home-login-btn"
            />
            <primary-button
              :label="$t('label.signUpForBeta')"
              @click="signUp"
              :title="$t('label.signUpForBeta')"
              data-testid="home-sign-up-beta-btn"
            />
          </template>
          <template v-else>
            <primary-button
              :label="$t('label.continue')"
              @click="enter"
              :title="$t('label.continue')"
              data-testid="home-continue-btn"
            />
          </template>
        </div>
      </div>
      <div class="bg-container">
        <!-- Padding top is rounded up aspect ratio percentage (height / width) of image -->
        <div :class="{'dark': isDarkMode}"></div>
      </div>
    </section>
    <section class="second-section-container">
      <h2>
        {{ $t('text.homepage.sectionHeader') }}
      </h2>
      <section>
        <info-box :title="$t('text.homepage.planEventTitle')">
          {{ $t('text.homepage.planEventBody') }}
        </info-box>
        <info-box :title="$t('text.homepage.setAvailabilityTitle')">
          {{ $t('text.homepage.setAvailabilityBody') }}
        </info-box>
        <info-box :title="$t('text.homepage.shareWithOthersTitle')">
          {{ $t('text.homepage.shareWithOthersBody') }}
        </info-box>
      </section>
    </section>
    <section class="third-section-container" :class="{'dark': isDarkMode}">
      <div class="content">
        <img
          :class="{'hidden': isDarkMode}"
          src="@/assets/img/homepage-screenshot.png"
          :alt="$t('text.homepage.screenshotCalendarAlt')"
        />
        <img
          class="hidden"
          :class="{'block': isDarkMode}"
          src="@/assets/img/homepage-screenshot-dark.png"
          :alt="$t('text.homepage.screenshotCalendarAlt')"
        />
        <div class="text-container">
          <p>{{ $t('text.homepage.calendarCopy') }}</p>
        </div>
      </div>
    </section>
    <section class="fourth-section-container">
      <div class="content" :class="{'dark': isDarkMode}">
        <img
          :class="{'hidden': isDarkMode}"
          src="@/assets/img/homepage-screenshot-2.png"
          :alt="$t('text.homepage.screenshotScheduleAlt')"
        />
        <img
          class="hidden"
          :class="{'block': isDarkMode}"
          src="@/assets/img/homepage-screenshot-2-dark.png"
          :alt="$t('text.homepage.screenshotScheduleAlt')"
        />
        <div class="text-container">
          <p>{{ $t('text.homepage.scheduleCopy') }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

section {
  color: var(--colour-ti-secondary); 
}

.hidden {
  display: none;
}

.block {
  display: block;
}

.first-section-container {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 3rem;
  margin-block-start: 2rem;

  .art-logo {
    margin-block-end: -3rem;
    width: 100%;
    max-width: 20rem;
  }

  .content {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-block-end: -3rem;

    h4 {
      max-width: 42rem;
      padding-block-start: 3rem;
      text-align: center;
      font-size: 1.25rem;
      font-weight: 300;
      line-height: 2.25rem;
      letter-spacing: 0.025em;
    }
  }

  .button-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin-block-start: 4rem;
    margin-block-end: 1rem;
  }

  .bg-container {
    width: 100%;

    & :first-child {
      height: 0px;
      width: 100%;
      background-image: url(@/assets/svg/homepage-split.svg);
      background-size: contain;
      background-repeat: no-repeat;
      padding-block-start: 14%;

      &.dark {
        background-image: url(@/assets/svg/homepage-split-dark.svg);
      }
    }
  }
}

.second-section-container {
  h2 {
    color: var(--colour-apmt-secondary);
    padding-block: 4rem;
    text-align: center;
    font-size: 1.875rem;
    line-height: 2.25rem;
  }

  section {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 4rem;
    max-width: 100%;
    margin-inline: auto;
  }
}

.third-section-container {
  width: 100%;
  background-image: url(@/assets/svg/homepage-wave.svg);
  background-size: cover;
  background-position: top;
  background-repeat: no-repeat;

  &.dark {
    background-image: url(@/assets/svg/homepage-wave-dark.svg);
  }

  .content {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-block-start: 13%;
    position: relative;
    margin-inline: auto;
    width: 100%;

    img {
      margin-block: auto;
      width: 100%;
      height: 100%;
      box-shadow: 3px 3px 16px 0 rgba(0, 0, 0, 0.04);
    }

    .text-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin-block: 5rem;

      p {
        width: 70%;
        font-size: 1.5rem;
        font-weight: 300;
        line-height: 2;
        letter-spacing: 0.025em;
      }
    }
  }
}

.fourth-section-container {
  width: 100%;
  padding-block-start: 8rem;

  .content {
    position: relative;
    margin-inline: auto;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 100%;
    padding-block-start: 5%;
    padding-block-end: 2rem;
    background-image: url(@/assets/svg/homepage-wave-bottom.svg);
    background-size: cover;
    background-position: top;
    background-repeat: no-repeat;

    &.dark {
      background-image: url(@/assets/svg/homepage-wave-bottom-dark.svg);
    }

    img {
      margin-block: auto;
      width: 100%;
      height: 100%;
      box-shadow: 3px 3px 16px 0 rgba(0, 0, 0, 0.04);
    }

    .text-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin-block: 5rem;

      p {
        width: 70%;
        font-size: 1.5rem;
        line-height: 2;
        font-weight: 300;
        letter-spacing: 0.025em;
      }
    }
  }
}

@media (--md) {
  .first-section-container {
    .art-logo {
      max-width: 24rem;
    }

    .content {
      margin-block-end: -5rem;
    }
  }

  .second-section-container {
    section {
      max-width: 80rem;
      flex-direction: row;
    }
  }

  .third-section-container {
    .content {
      flex-direction: row;

      img {
        width: 50%;
      }

      .text-container {
        width: 45%;
      }
    }
  }

  .fourth-section-container {
    .content {
      flex-direction: row-reverse;

      img {
        width: 50%;
      }

      .text-container {
        width: 45%;
      }
    }
  }
}

@media (--lg) {
  .first-section-container {
    .art-logo {
      max-width: 28rem;
    }

    .content {
      margin-block-end: -7rem;
    }
  }
}

@media (--xl) {
  .first-section-container {
    .content {
      margin-block-end: -10rem;
    }
  }
}
</style>
