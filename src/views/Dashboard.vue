<template>
  <!-- ...existing code... -->
  <div class="right-column">
    <section class="upcoming">
      <div class="upcoming-header">
        <h3>Upcoming</h3>
        <!-- changed code -->
        <button
          class="toggle-upcoming"
          @click="toggleUpcoming"
          :aria-expanded="showUpcoming.toString()"
        >
          {{ showUpcoming ? 'Hide upcoming fixtures' : 'Show upcoming fixtures' }}
        </button>
        <!-- ...existing code... -->
      </div>

      <!-- changed code: wrap content in animated container -->
      <div
        class="upcoming-panel"
        :class="{ open: showUpcoming }"
        role="region"
        aria-hidden="!showUpcoming"
      >
        <!-- future fixtures content -->
        <div class="future-fixtures">
          <!-- ...existing code for fixtures ... -->
        </div>
      </div>
      <!-- ...existing code... -->
    </section>
  </div>
  <!-- ...existing code... -->
</template>

<script>
export default {
  // ...existing code...
  data() {
    return {
      // ...existing code...
      showUpcoming: false, // single boolean controlling both label and panel
    }
  },
  methods: {
    // ...existing code...
    toggleUpcoming() {
      this.showUpcoming = !this.showUpcoming
    }
  }
  // ...existing code...
}
</script>

<style scoped>
/* changed code: animated expand/collapse to avoid layout jump */
.upcoming-panel {
  max-height: 0;
  overflow: hidden;
  transition: max-height 380ms cubic-bezier(.25,.8,.25,1), padding 200ms;
  padding: 0 1.25rem;
  background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 100%);
}

/* when open, give enough max-height for content; use large value to accommodate variable content */
.upcoming-panel.open {
  max-height: 520px; /* adjust to expected content size or compute dynamically */
  padding: 1rem 1.25rem 1.5rem;
}

/* small visual for the toggle button to match UI */
.toggle-upcoming {
  border-radius: 10px;
  padding: .5rem .9rem;
  background: #0f2740;
  color: #fff;
  border: 2px solid rgba(255,255,255,.15);
}
</style>