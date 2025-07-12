/*let idx=0;
const slides=document.querySelectorAll('.slide');
function showSlide(i){
  slides.forEach(s=>s.classList.remove('active'));
  slides[i].classList.add('active');
}
function nextSlide(){
  idx=(idx+1)%slides.length;
  showSlide(idx);
}
setInterval(nextSlide,3000);
*/

// mobile nav toggle
function toggleMenu(){
  document.querySelector('.nav-links').classList.toggle('show');
}
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', () => {
    navMenu.classList.remove('active');
  });
});